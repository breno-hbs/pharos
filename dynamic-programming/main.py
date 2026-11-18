"""Pharos - interface de linha de comando e menu interativo.

Este arquivo só cuida de entrada e saída. Os cálculos ficam no pacote
`pharos/` (funções e classes que recebem parâmetros e devolvem resultados).

Sem argumentos, abre o menu interativo:
  python main.py

Comandos diretos:
  python main.py consultar 13211 407 --hora 07:00
  python main.py consultar 13211 407 --criterio distancia --cenario UTIL_TARDE
  python main.py criterios 1325 407
  python main.py paradas --busca "carlos lacerda"
  python main.py desempenho
  python main.py exportar --cenarios UTIL_MANHA,UTIL_TARDE
  python main.py extrair --gtfs artesp_gtfs.zip
"""
import argparse
import os
import sys

from pharos import config
from pharos.alternativas import Consultor, resumo_texto
from pharos.grafo import carregar_rede

BASE = os.path.dirname(os.path.abspath(__file__))
REDE = os.path.join(BASE, "dados", "rede_piloto.json")


# ------------------------------------------------------------ apresentação
def texto_simulacao(cons, resultado, hora):
    """Linhas de texto com a simulação no quadro de horários."""
    linhas = [f"\n  Simulação no quadro de horários ({cons.g.service_id}) saindo às {hora}:"]
    for k, alt in enumerate(resultado["alternativas"], 1):
        s = cons.simular(alt, hora)
        if s["viavel"]:
            passos = "; ".join(f"{p['linha']} {p['partida']}->{p['chegada']}" for p in s["passos"])
            linhas.append(f"    alternativa {k}: {passos} (total {s['duracao_min']} min)")
        else:
            linhas.append(f"    alternativa {k}: inviável - {s['motivo']}")
    return "\n".join(linhas)


def texto_criterios(cons, origem, destino):
    """Tabela com o caminho mínimo de cada critério."""
    A = cons.g.arestas
    linhas = [f"{origem} {cons.g.nome(origem)} -> {destino} {cons.g.nome(destino)}",
              f"{'critério':<10} {'linhas':<22} {'baldeações':>10} {'tempo (min)':>12} {'distância (km)':>15}"]
    for c in config.CRITERIOS:
        cam = cons.melhor_caminho(origem, destino, c)
        if cam is None:
            linhas.append(f"{c:<10} sem caminho")
            continue
        t = sum(A[x].peso("tempo") for x in cam) / 60
        d = sum(A[x].distancia_m for x in cam) / 1000
        linhas.append(f"{c:<10} {' + '.join(A[x].linha for x in cam):<22} {len(cam) - 1:>10} {t:>12.1f} {d:>15.2f}")
    return "\n".join(linhas)


def texto_desempenho(rede, cenario, repeticoes=3):
    """Mede e descreve a eficiência do Floyd-Warshall na rede piloto."""
    from pharos import desempenho as dz
    from pharos.grafo import Grafo
    g = Grafo(rede, cenario)
    tam = g.tamanho()
    n = tam["vertices"]
    out = [f"Grafo ({config.CENARIOS[cenario]['descricao']}): {n} vértices, {tam['arestas']} arestas "
           f"(viagens u->v em uma linha), {tam['pares_com_aresta']} pares (u, v) com aresta",
           "",
           "1) Floyd-Warshall x Dijkstra de cada origem (heapq), mesma matriz de custos",
           f"{'critério':<10} {'FW Python':>10} {'FW NumPy':>10} {'Dijkstra xV':>12}  resultados iguais"]
    for c in config.CRITERIOS:
        W, _ = g.matriz(c)
        r = dz.comparar(W, repeticoes)
        ok = "sim" if r["python_igual_numpy"] and r["python_igual_dijkstra"] else "NÃO"
        out.append(f"{c:<10} {r['fw_python_s']:>9.3f}s {r['fw_numpy_s']:>9.3f}s {r['dijkstra_todos_s']:>11.3f}s  {ok}")
    out += ["",
            f"   Teoria: Floyd-Warshall faz V³ = {r['operacoes_fw']:,} relaxações; Dijkstra xV faz da ordem de",
            f"   V·(V+E)·log V = {r['operacoes_dijkstra']:,} operações (E = {r['arestas']:,} pares com aresta).",
            f"   Pares com caminho: {r['pares_alcancaveis']:,} de {n * (n - 1):,}.",
            "",
            "2) Crescimento: subgrafos com os k primeiros vértices",
            f"{'k':>5} {'FW Python':>10} {'FW NumPy':>10} {'ns/k³ NumPy':>12}"]
    W, _ = g.matriz("tempo")
    for lin in dz.crescimento(W, [30, 60, 120, 180, n], repeticoes):
        out.append(f"{lin['k']:>5} {lin['fw_python_s']:>9.4f}s {lin['fw_numpy_s']:>9.4f}s {lin['ns_por_k3_numpy']:>12.2f}")
    out += ["",
            "3) As três versões vistas em aula, na rede real (subgrafos com k vértices)",
            f"{'k':>4} {'recursão: chamadas':>20} {'tempo':>8} {'memo: estados':>15} {'tempo':>8} "
            f"{'tabela: células':>16} {'tempo':>8}  iguais"]
    for lin in dz.versoes_do_curso(W):
        rec = (f"{lin['recursao_chamadas']:>20,} {lin['recursao_s']:>7.3f}s" if "recursao_s" in lin
               else f"{'(inviável: ~3^k)':>20} {'-':>8}")
        memo = f"{lin['memo_estados']:>15,} {lin['memo_s']:>7.3f}s" if "memo_s" in lin else f"{'-':>15} {'-':>8}"
        iguais = all(lin.get(c, True) for c in ("memo_igual", "recursao_igual"))
        out.append(f"{lin['k']:>4} {rec} {memo} {lin['tabela_celulas']:>16,} {lin['tabela_s']:>7.3f}s  "
                   f"{'sim' if iguais else 'NÃO'}")
    out.append("   A recursão recalcula subproblemas; a memoização resolve isso, mas guarda V²·(V+1) estados;"
               "\n   a tabela bottom-up guarda só V² células e é a versão usada pelo Pharos.")
    p = dz.projecao_gtfs_completo()
    out += ["",
            f"4) GTFS completo ({p['vertices']:,} paradas): {p['relaxacoes']:.1e} relaxações e "
            f"{p['bytes_por_matriz'] / 1e9:.1f} GB por matriz -> inviável; por isso o recorte piloto.",
            "   Memória no piloto: 2 matrizes (D e NXT) x V² = "
            f"{2 * n * n:,} valores por critério."]
    return "\n".join(out)


# ------------------------------------------------------------ comandos
def cmd_consultar(a):
    cons = Consultor(carregar_rede(REDE), a.cenario)
    r = cons.alternativas(a.origem, a.destino, a.criterio)
    print(resumo_texto(cons, r))
    if a.hora and r["alternativas"]:
        print(texto_simulacao(cons, r, a.hora))


def cmd_criterios(a):
    print(texto_criterios(Consultor(carregar_rede(REDE), a.cenario), a.origem, a.destino))


def cmd_paradas(a):
    rede = carregar_rede(REDE)
    termo = (a.busca or "").lower()
    for s, p in sorted(rede["paradas"].items(), key=lambda x: x[1]["nome"]):
        if p["no_recorte"] and termo in p["nome"].lower():
            print(f"{s:>6}  {p['nome']}{' *MVP*' if s in config.PONTOS_MVP else ''}")


def cmd_desempenho(a):
    print(texto_desempenho(carregar_rede(REDE), a.cenario))


def cmd_exportar(a):
    from pharos.exportar import exportar
    cen = [c.strip().upper() for c in a.cenarios.split(",")] if a.cenarios else None
    exportar(carregar_rede(REDE), os.path.join(BASE, "saida"), cen, criterio=a.criterio,
             data_calculo=a.data_calculo)


def cmd_extrair(a):
    from pharos.extracao_gtfs import extrair
    extrair(a.gtfs, REDE)


# ------------------------------------------------------------ menu
MENU = """
==================== PHAROS · rede piloto ARTESP ====================
 1) Comparar alternativas entre dois pontos
 2) Comparar critérios (tempo x distância x embarques)
 3) Procurar parada pelo nome
 4) Medir a eficiência do Floyd-Warshall
 0) Sair"""


def escolher_ponto(entrada, saida, titulo):
    """Mostra os pontos do MVP e devolve um stop_id (número da lista ou id)."""
    ids = list(config.PONTOS_MVP)
    saida(f"\n{titulo}")
    for k, s in enumerate(ids, 1):
        saida(f"  {k:>2}) [{s:>5}] {config.PONTOS_MVP[s]}")
    valor = entrada("Número da lista ou stop_id: ").strip()
    if valor.isdigit() and 1 <= int(valor) <= len(ids):
        return ids[int(valor) - 1]
    if valor:
        return valor                     # stop_id digitado; validado pelo Consultor
    raise ValueError("nenhum ponto informado")


def escolher_opcao(entrada, saida, titulo, opcoes, padrao):
    """Escolha numerada; Enter vazio devolve o padrão."""
    saida(f"\n{titulo}")
    for k, o in enumerate(opcoes, 1):
        saida(f"  {k}) {o}{' (padrão)' if o == padrao else ''}")
    valor = entrada("Opção: ").strip()
    if not valor:
        return padrao
    if valor.isdigit() and 1 <= int(valor) <= len(opcoes):
        return opcoes[int(valor) - 1]
    raise ValueError(f"opção inválida: {valor!r}")


def menu(entrada=input, saida=print):
    """Laço do menu. `entrada` e `saida` podem ser trocadas nos testes."""
    rede = carregar_rede(REDE)
    consultores = {}                     # cenário -> Consultor (Floyd-Warshall calculado uma vez)

    def consultor(cenario):
        if cenario not in consultores:
            saida("Calculando Floyd-Warshall para o cenário...")
            consultores[cenario] = Consultor(rede, cenario)
        return consultores[cenario]

    while True:
        saida(MENU)
        try:
            op = entrada("Opção: ").strip()
        except (EOFError, KeyboardInterrupt):
            saida("\nAté logo.")
            return
        try:
            if op == "0":
                saida("Até logo.")
                return
            if op in ("1", "2"):
                o = escolher_ponto(entrada, saida, "ORIGEM")
                d = escolher_ponto(entrada, saida, "DESTINO")
                cen = escolher_opcao(entrada, saida, "Cenário", list(config.CENARIOS), config.CENARIO_PADRAO)
                cons = consultor(cen)
                if op == "2":
                    saida(texto_criterios(cons, o, d))
                    continue
                crit = escolher_opcao(entrada, saida, "Ordenar por", list(config.CRITERIOS), "tempo")
                r = cons.alternativas(o, d, crit)
                saida(resumo_texto(cons, r))
                hora = entrada("\nSimular a partir de qual horário? (HH:MM ou Enter para pular): ").strip()
                if hora and r["alternativas"]:
                    saida(texto_simulacao(cons, r, hora))
            elif op == "3":
                termo = entrada("Parte do nome: ").strip().lower()
                achadas = [(s, p["nome"]) for s, p in sorted(rede["paradas"].items())
                           if p["no_recorte"] and termo in p["nome"].lower()]
                for s, nome in achadas[:30]:
                    saida(f"  {s:>6}  {nome}")
                saida(f"  {len(achadas)} parada(s) encontrada(s)" + (" (mostrando 30)" if len(achadas) > 30 else ""))
            elif op == "4":
                saida(texto_desempenho(rede, config.CENARIO_PADRAO, repeticoes=1))
            else:
                saida("Opção inválida.")
        except KeyError as e:
            saida(f"Erro: {e.args[0]}. Use a opção 3 para procurar o stop_id.")
        except ValueError as e:
            saida(f"Erro: {e}")
        except (EOFError, KeyboardInterrupt):
            saida("\nAté logo.")
            return


# ------------------------------------------------------------ entrada
def criar_parser():
    p = argparse.ArgumentParser(description="Pharos - Floyd-Warshall na rede piloto ARTESP "
                                            "(sem argumentos abre o menu interativo)")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("extrair", help="regenera dados/rede_piloto.json a partir do GTFS")
    s.add_argument("--gtfs", required=True)
    s.set_defaults(f=cmd_extrair)
    for nome, f in (("consultar", cmd_consultar), ("criterios", cmd_criterios)):
        s = sub.add_parser(nome)
        s.add_argument("origem")
        s.add_argument("destino")
        s.add_argument("--cenario", default=config.CENARIO_PADRAO, type=str.upper, choices=list(config.CENARIOS))
        if nome == "consultar":
            s.add_argument("--criterio", default="tempo", choices=config.CRITERIOS)
            s.add_argument("--hora", help="HH:MM para simular no quadro de horários")
        s.set_defaults(f=f)
    s = sub.add_parser("paradas")
    s.add_argument("--busca")
    s.set_defaults(f=cmd_paradas)
    s = sub.add_parser("desempenho")
    s.add_argument("--cenario", default=config.CENARIO_PADRAO, type=str.upper, choices=list(config.CENARIOS))
    s.set_defaults(f=cmd_desempenho)
    s = sub.add_parser("exportar")
    s.add_argument("--cenarios", help=f"lista separada por vírgulas (padrão: {config.CENARIO_PADRAO})")
    s.add_argument("--criterio", default="tempo", choices=config.CRITERIOS)
    s.add_argument("--data-calculo", help="data gravada em dt_calculo, AAAA-MM-DD (padrão: hoje)")
    s.set_defaults(f=cmd_exportar)
    return p


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        if not argv:
            menu()
            return 0
        a = criar_parser().parse_args(argv)
        a.f(a)
        return 0
    except KeyError as e:
        print(f"Erro: {e.args[0]}. Use `python main.py paradas --busca <nome>` para achar o stop_id.",
              file=sys.stderr)
    except (FileNotFoundError, ValueError) as e:
        print(f"Erro: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nInterrompido.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
