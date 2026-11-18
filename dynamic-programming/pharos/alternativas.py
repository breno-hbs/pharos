"""Consulta de alternativas origem→destino a partir das tabelas do Floyd-Warshall.

Por que todos os pares (Floyd-Warshall) e não uma busca por consulta:
a tabela D contém o melhor custo de QUALQUER parada até o destino. Assim, a
melhor viagem que começa embarcando na linha p em `o` é
    min_x [ peso(o→x pela linha p) + D[x][destino] ]
e a que termina desembarcando da linha q em `d` é
    min_y [ D[origem][y] + peso(y→d pela linha q) ].
Isso gera, com consultas O(1) à tabela, a melhor opção de cada linha que atende
a origem ou o destino, além do ótimo de cada critério.

Depois, os candidatos são:
 1. unificados quando percorrem os mesmos itinerários (mesmas paradas), mesmo
    que por linhas diferentes: linhas no mesmo itinerário = uma alternativa;
 2. ordenados pelo critério escolhido;
 3. filtrados por distinção geométrica: um candidato que fica >= 80% sobre o
    traçado de uma alternativa já aceita é tratado como variante dela.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

import numpy as np

from . import config
from .floyd_warshall import floyd_warshall, floyd_warshall_numpy, reconstruir
from .geo import fracao_proxima, para_lonlat, para_xy
from .grafo import Grafo, hhmm_para_s, s_para_hhmm


@dataclass
class Trecho:
    linha: str
    padrao: str
    linhas_equivalentes: tuple   # todas as linhas com o mesmo itinerário u→v no cenário
    embarque: str
    desembarque: str
    paradas: list                # da parada de embarque à de desembarque, inclusive
    espera_s: float
    bordo_s: float
    distancia_m: float
    partidas_linha: int          # partidas da linha usada em u na janela
    partidas_combinadas: int     # partidas de todas as linhas equivalentes


@dataclass
class Alternativa:
    origem: str
    destino: str
    trechos: list
    arestas: list
    xy: np.ndarray
    geradores: set = field(default_factory=set)

    @property
    def chave(self):
        return tuple((t.embarque, t.desembarque, tuple(t.paradas)) for t in self.trechos)

    @property
    def embarques(self):
        return len(self.trechos)

    @property
    def baldeacoes(self):
        return max(0, len(self.trechos) - 1)

    @property
    def pontos_baldeacao(self):
        return [t.embarque for t in self.trechos[1:]]

    # math.fsum: soma exatamente arredondada, igual em qualquer versão do Python
    # (o sum() de floats mudou no 3.12) e em qualquer ordem dos trechos.
    @property
    def espera_s(self):
        return math.fsum(t.espera_s for t in self.trechos)

    @property
    def bordo_s(self):
        return math.fsum(t.bordo_s for t in self.trechos)

    @property
    def tempo_s(self):
        return self.espera_s + self.bordo_s

    @property
    def distancia_m(self):
        return math.fsum(t.distancia_m for t in self.trechos)

    @property
    def paradas(self):
        seq = []
        for t in self.trechos:
            seq.extend(t.paradas if not seq else t.paradas[1:])
        return seq

    def custo(self, criterio):
        if criterio == "tempo":
            return self.tempo_s
        if criterio == "distancia":
            return self.distancia_m + config.EPS_EMBARQUE_M * self.embarques
        if criterio == "embarques":
            return self.embarques + config.EPS_DISTANCIA_EMB * self.distancia_m
        raise ValueError(criterio)

    def lonlat(self):
        return para_lonlat(self.xy).round(6).tolist()


class Consultor:
    """Pré-calcula Floyd-Warshall para os três critérios e responde consultas."""

    def __init__(self, rede: dict, cenario: str = config.CENARIO_PADRAO, implementacao: str = "python"):
        """implementacao='python' usa o Floyd-Warshall em Python puro (padrão,
        é o algoritmo avaliado); 'numpy' usa a versão vetorizada, idêntica."""
        if implementacao not in ("python", "numpy"):
            raise ValueError("implementacao deve ser 'python' ou 'numpy'")
        self.g = Grafo(rede, cenario)
        self.cenario = cenario
        self.W, self.arg, self.D, self.NXT, self.tempos_fw = {}, {}, {}, {}, {}
        fw = floyd_warshall_numpy if implementacao == "numpy" else floyd_warshall
        for c in config.CRITERIOS:
            W, arg = self.g.matriz(c)
            t0 = time.perf_counter()
            D, NXT = fw(W)
            self.tempos_fw[c] = time.perf_counter() - t0
            self.W[c], self.arg[c] = W, arg
            self.D[c] = np.asarray(D, dtype=float)
            self.NXT[c] = np.asarray(NXT, dtype=np.int64)

    # ------------------------------------------------------------ montagem
    def _trecho(self, ai: int) -> Trecho:
        a = self.g.arestas[ai]
        eq = tuple(sorted({e.linha for e in self.g.equivalentes(a)}))
        return Trecho(linha=a.linha, padrao=a.padrao, linhas_equivalentes=eq, embarque=a.u,
                      desembarque=a.v, paradas=[a.u, *a.intermediarias, a.v], espera_s=a.espera_s,
                      bordo_s=a.bordo_s, distancia_m=a.distancia_m, partidas_linha=a.n_partidas,
                      partidas_combinadas=self.g.partidas_combinadas(a))

    def _alternativa(self, o, d, arestas, gerador) -> Alternativa:
        xy = np.vstack([self.g.xy_aresta(self.g.arestas[ai]) for ai in arestas])
        return Alternativa(o, d, [self._trecho(ai) for ai in arestas], list(arestas), xy, {gerador})

    def _arestas_do_caminho(self, criterio, caminho):
        return [self.arg[criterio][(a, b)] for a, b in zip(caminho, caminho[1:])]

    def _indices(self, o, d):
        for s in (o, d):
            if s not in self.g.idx:
                raise KeyError(f"parada {s} fora da rede piloto")
        return self.g.idx[o], self.g.idx[d]

    def melhor_caminho(self, o: str, d: str, criterio: str):
        """Lista de arestas do caminho mínimo, ou None se não houver caminho."""
        i, j = self._indices(o, d)
        cam = reconstruir(self.NXT[criterio], i, j)
        return None if cam is None else self._arestas_do_caminho(criterio, cam)

    def valido(self, arestas) -> bool:
        """Rejeita caminhos com baldeação inútil ou parada repetida.

        Baldeação inútil: dois trechos seguidos no mesmo padrão de viagem (o
        passageiro desceria e subiria no mesmo serviço). Parada repetida: laço.
        Pelo modelo de custos, nenhum ótimo do Floyd-Warshall viola isso; a
        verificação protege os candidatos construídos por combinação.
        """
        A = self.g.arestas
        for x, y in zip(arestas, arestas[1:]):
            if A[x].padrao == A[y].padrao:
                return False
        seq = []
        for ai in arestas:
            a = A[ai]
            seq.extend([a.u, *a.intermediarias, a.v] if not seq else [*a.intermediarias, a.v])
        return len(seq) == len(set(seq))

    # ------------------------------------------------------------ consulta
    def alternativas(self, o: str, d: str, criterio: str = "tempo", maximo: int = config.MAX_ALTERNATIVAS):
        if criterio not in config.CRITERIOS:
            raise ValueError(f"critério deve ser um de {config.CRITERIOS}")
        i, j = self._indices(o, d)
        base = {"criterio": criterio, "cenario": self.cenario, "origem": o, "destino": d}
        if o == d:
            return {**base, "status": "ORIGEM_IGUAL_DESTINO", "alternativas": [], "variantes": []}
        cands = {}

        def add(arestas, gerador):
            alt = self._alternativa(o, d, arestas, gerador)
            atual = cands.get(alt.chave)
            if atual is None:
                cands[alt.chave] = alt
            else:
                alt.geradores |= atual.geradores
                if alt.custo(criterio) < atual.custo(criterio):
                    cands[alt.chave] = alt
                else:
                    atual.geradores |= alt.geradores

        # (1) ótimo de cada critério
        for c in config.CRITERIOS:
            cam = self.melhor_caminho(o, d, c)
            if cam is not None and self.valido(cam):
                add(cam, f"otimo_{c}")
        # (2) todo itinerário direto o→d
        for ai in self.g.saindo.get(o, []):
            if self.g.arestas[ai].v == d:
                add([ai], "direto")
        Dt, Nt, idx, A = self.D[criterio], self.NXT[criterio], self.g.idx, self.g.arestas
        # (3) melhor opção válida embarcando em cada linha que atende a origem
        por_padrao = {}
        for ai in self.g.saindo.get(o, []):
            x = idx[A[ai].v]
            if np.isfinite(Dt[x, j]):
                por_padrao.setdefault(A[ai].padrao, []).append((A[ai].peso(criterio) + Dt[x, j], ai))
        for pid, opcoes in por_padrao.items():
            for _, ai in sorted(opcoes):
                resto = [] if A[ai].v == d else self._arestas_do_caminho(criterio, reconstruir(Nt, idx[A[ai].v], j))
                if self.valido([ai] + resto):
                    add([ai] + resto, f"embarque_{A[ai].linha}")
                    break
        # (4) melhor opção válida desembarcando de cada linha que atende o destino
        por_padrao = {}
        for ai in self.g.chegando.get(d, []):
            y = idx[A[ai].u]
            if np.isfinite(Dt[i, y]):
                por_padrao.setdefault(A[ai].padrao, []).append((Dt[i, y] + A[ai].peso(criterio), ai))
        for pid, opcoes in por_padrao.items():
            for _, ai in sorted(opcoes):
                ini = [] if A[ai].u == o else self._arestas_do_caminho(criterio, reconstruir(Nt, i, idx[A[ai].u]))
                if self.valido(ini + [ai]):
                    add(ini + [ai], f"desembarque_{A[ai].linha}")
                    break

        if not cands:
            return {**base, "status": "SEM_TRAJETO", "alternativas": [], "variantes": [], "filtradas": []}
        reta = self.linha_reta_m(o, d)
        base["linha_reta_m"] = reta
        ordenadas = sorted(cands.values(), key=lambda a: (a.custo(criterio), a.embarques, a.chave))
        aceitas, variantes, filtradas = [], [], []
        for a in ordenadas:
            desvio = a.distancia_m / reta if reta > 0 else float("inf")
            if a.baldeacoes > config.MAX_BALDEACOES or desvio > config.MAX_INDICE_DESVIO:
                filtradas.append({"alternativa": a, "baldeacoes": a.baldeacoes, "indice_desvio": desvio})
                continue
            parecida = None
            for k, b in enumerate(aceitas):
                s = self.sobreposicao(a, b)
                if s >= config.LIMIAR_SOBREPOSICAO:
                    parecida = (k, s)
                    break
            if parecida:
                variantes.append({"alternativa": a, "parecida_com": parecida[0], "sobreposicao": parecida[1]})
            elif len(aceitas) < maximo:
                aceitas.append(a)
            else:
                variantes.append({"alternativa": a, "parecida_com": None, "sobreposicao": None})
        matriz = [[1.0 if p == q else self.sobreposicao(aceitas[p], aceitas[q]) for q in range(len(aceitas))]
                  for p in range(len(aceitas))]
        if not aceitas:
            status = "SEM_TRAJETO_RAZOAVEL"
        else:
            status = "ALTERNATIVAS_DISTINTAS" if len(aceitas) >= 2 else "TRAJETO_UNICO"
        return {**base, "status": status, "alternativas": aceitas, "variantes": variantes,
                "filtradas": filtradas, "sobreposicao": matriz}

    def linha_reta_m(self, o: str, d: str) -> float:
        a, b = self.g.paradas[o], self.g.paradas[d]
        xy = para_xy([a["lon"], b["lon"]], [a["lat"], b["lat"]])
        return float(np.hypot(*(xy[1] - xy[0])))

    @staticmethod
    def sobreposicao(a: Alternativa, b: Alternativa) -> float:
        """Maior fração de um traçado que fica a até RAIO_SOBREPOSICAO_M do outro."""
        r, p = config.RAIO_SOBREPOSICAO_M, config.PASSO_AMOSTRAGEM_M
        return max(fracao_proxima(a.xy, b.xy, r, p), fracao_proxima(b.xy, a.xy, r, p))

    # ------------------------------------------------------ validação horária
    def simular(self, alt: Alternativa, hora_saida: str, service_id: str | None = None):
        """Percorre o quadro de horários do GTFS a partir de `hora_saida`.

        Em cada trecho pega a primeira partida, de qualquer linha equivalente,
        igual ou posterior ao horário corrente. Mostra se a combinação de
        serviços existe na programação daquele tipo de dia. Os horários de
        passagem são os programados (interpolados) pela ARTESP.
        """
        sid = service_id or self.g.service_id
        inicio = t = hhmm_para_s(hora_saida)
        passos = []
        for tr in alt.trechos:
            opcoes = []
            for pid, p in sorted(self.g.padroes.items()):
                if p["route_id"] not in tr.linhas_equivalentes:
                    continue
                seq = p["paradas"]
                if tr.embarque not in seq or tr.desembarque not in seq:
                    continue
                a, b = seq.index(tr.embarque), seq.index(tr.desembarque)
                if seq[a:b + 1] != tr.paradas:
                    continue
                for t0 in p["partidas"].get(sid, []):
                    if t0 + p["offset_s"][a] >= t:
                        opcoes.append((t0 + p["offset_s"][a], t0 + p["offset_s"][b], p["route_id"]))
                        break
            if not opcoes:
                return {"viavel": False, "passos": passos,
                        "motivo": f"sem partida em {tr.embarque} a partir de {s_para_hhmm(t)} ({sid})"}
            dep, cheg, linha = min(opcoes)
            passos.append({"linha": linha, "embarque": tr.embarque, "partida": s_para_hhmm(dep),
                           "desembarque": tr.desembarque, "chegada": s_para_hhmm(cheg),
                           "espera_min": round((dep - t) / 60, 1)})
            t = cheg
        return {"viavel": True, "passos": passos, "duracao_min": round((t - inicio) / 60, 1)}


def resumo_texto(cons: Consultor, res: dict) -> str:
    """Texto legível de uma consulta (usado pela CLI)."""
    g = cons.g
    o, d = res["origem"], res["destino"]
    lin = [f"{o} {g.nome(o)}  ->  {d} {g.nome(d)}",
           f"Cenário: {config.CENARIOS[cons.cenario]['descricao']} | ordenação: {res['criterio']} | {res['status']}"]
    for k, a in enumerate(res["alternativas"], 1):
        lin.append(f"\n  Alternativa {k}: {a.embarques} embarque(s), {a.baldeacoes} baldeação(ões), "
                   f"{len(a.paradas)} paradas, {a.distancia_m / 1000:.2f} km, "
                   f"espera ~{a.espera_s / 60:.1f} + bordo {a.bordo_s / 60:.1f} = {a.tempo_s / 60:.1f} min")
        for t in a.trechos:
            outras = [x for x in t.linhas_equivalentes if x != t.linha]
            lin.append(f"    linha {t.linha}{' (mesmo itinerário: ' + ', '.join(outras) + ')' if outras else ''}: "
                       f"{t.embarque} -> {t.desembarque}, {len(t.paradas) - 1} saltos, {t.distancia_m:.0f} m, "
                       f"{t.partidas_linha} partidas da linha na janela ({t.partidas_combinadas} somando equivalentes)")
        if a.pontos_baldeacao:
            lin.append(f"    baldeação em: {', '.join(f'{s} {g.nome(s)[:40]}' for s in a.pontos_baldeacao)}")
        lin.append(f"    candidatos que geraram: {', '.join(sorted(a.geradores))}")
    if len(res["alternativas"]) > 1:
        lin.append(f"\n  Sobreposição (fração a até {config.RAIO_SOBREPOSICAO_M:.0f} m da outra):")
        for linha in res["sobreposicao"]:
            lin.append("    " + " ".join(f"{x:5.2f}" for x in linha))
    if res["status"] == "SEM_TRAJETO":
        lin.append("  Nenhuma combinação de linhas do piloto liga a origem ao destino "
                   "(baldeação a pé e trechos fora do recorte não são modelados).")
    if res.get("filtradas"):
        lin.append(f"\n  Omitidas pelos filtros (>{config.MAX_BALDEACOES} baldeações ou desvio "
                   f">{config.MAX_INDICE_DESVIO}x a linha reta de {res['linha_reta_m']:.0f} m): {len(res['filtradas'])}")
        for f in res["filtradas"][:3]:
            a = f["alternativa"]
            lin.append(f"    {' + '.join(t.linha for t in a.trechos)}: {a.distancia_m / 1000:.1f} km, "
                       f"{f['baldeacoes']} baldeação(ões), desvio {f['indice_desvio']:.1f}x")
    if res["variantes"]:
        lin.append(f"\n  Variantes descartadas: {len(res['variantes'])}")
        for v in res["variantes"][:4]:
            a = v["alternativa"]
            motivo = (f"{v['sobreposicao']:.0%} sobre a alternativa {v['parecida_com'] + 1}"
                      if v["parecida_com"] is not None else "acima do máximo de alternativas")
            lin.append(f"    {' + '.join(t.linha for t in a.trechos)}: {motivo}")
    return "\n".join(lin)
