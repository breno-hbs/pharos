"""Exporta as alternativas pré-calculadas no formato do banco Pharos (Oracle).

Os seis CSVs principais têm o nome e as colunas das tabelas de
database/02_ddl.sql (repositório da equipe), sem as chaves substitutas
(id_*, IDENTITY no Oracle). Cada chave estrangeira sai pela chave natural
(coluna UNIQUE) da tabela referenciada, que a carga converte em id:

  id_cenario -> cd_cenario      id_parada_* -> cd_parada_*      id_linha -> cd_linha
  id_fonte   -> nm_fonte        id_par_od   -> (cd_cenario, cd_parada_origem, cd_parada_destino)
  id_alternativa -> (cd_cenario, cd_parada_origem, cd_parada_destino, nr_ordem)

  ph_cenario.csv              os cinco cenários (iguais ao DML do banco)
  ph_parada.csv               paradas usadas nos pares e nas etapas
  ph_linha.csv                linhas da rede piloto
  ph_par_origem_destino.csv   resultado de cada par origem-destino por cenário
  ph_alternativa.csv          até 3 alternativas por par (minutos e km)
  ph_etapa_trajeto.csv        uma etapa por embarque

Complementares (não são tabelas do banco), em complementar/:
  alternativa_detalhe.csv  segundos, espera, índice de desvio, sobreposição
  etapa_detalhe.csv        linhas equivalentes e partidas na janela
  sequencia_paradas.csv    todas as paradas de cada alternativa, com coordenadas
  alternativas.geojson     uma LineString por alternativa, para o mapa
E metadados.json: fonte, versão do GTFS, parâmetros e regras de conversão.
"""
from __future__ import annotations

import csv
import json
import os
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from . import config
from .alternativas import Consultor

# O banco guarda só três situações; o detalhe do Python fica no metadados.
STATUS_BANCO = {
    "ALTERNATIVAS_DISTINTAS": "COM_ALTERNATIVAS",
    "TRAJETO_UNICO": "COM_ALTERNATIVAS",
    "SEM_TRAJETO": "SEM_TRAJETO",
    "SEM_TRAJETO_RAZOAVEL": "SEM_TRAJETO_RAZOAVEL",
}

MUNICIPIOS = ("Itapecerica da Serra", "Embu das Artes", "Taboão da Serra", "São Paulo")
_CIDADE_NO_NOME = re.compile(r",\s*([^,]+?)\s*-\s*SP\b")

CHAVE_ALTERNATIVA = ["cd_cenario", "cd_parada_origem", "cd_parada_destino", "nr_ordem"]


def _csv(caminho, cabecalho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)


def decimal_texto(valor: float, casas: int) -> str:
    """Arredonda meio para cima (como o Oracle faz em NUMBER(p,s)) e fixa as casas."""
    q = Decimal(1).scaleb(-casas)
    return str(Decimal(str(float(valor))).quantize(q, rounding=ROUND_HALF_UP))


def municipio(cd_parada: str, nome: str) -> tuple:
    """(município, origem da informação). Não infere pela vizinhança."""
    for trecho in reversed(_CIDADE_NO_NOME.findall(nome)):
        for m in MUNICIPIOS:
            if trecho.endswith(m):
                return m, "nome_gtfs"
    if cd_parada in config.MUNICIPIO_CONFERIDO:
        return config.MUNICIPIO_CONFERIDO[cd_parada], "conferido"
    return config.MUNICIPIO_NAO_INFORMADO, "nao_informado"


def _ordem_codigo(cd: str):
    return (0, int(cd), cd) if cd.isdigit() else (1, 0, cd)


def exportar(rede: dict, pasta: str, cenarios=None, pontos=None, criterio="tempo",
             data_calculo: str | None = None, verbose=True) -> dict:
    log = print if verbose else (lambda *a, **k: None)
    cenarios = list(cenarios or [config.CENARIO_PADRAO])
    for c in cenarios:
        if c not in config.CENARIOS:
            raise ValueError(f"cenário desconhecido: {c}. Opções: {', '.join(config.CENARIOS)}")
    pontos = list(pontos or config.PONTOS_MVP)
    for p in pontos:
        if p not in rede["paradas"]:
            raise ValueError(f"parada {p} não existe na rede piloto")
    data_calculo = data_calculo or date.today().isoformat()
    try:
        date.fromisoformat(data_calculo)
    except ValueError:
        raise ValueError(f"data de cálculo deve estar no formato AAAA-MM-DD: {data_calculo}") from None
    comp = os.path.join(pasta, "complementar")
    os.makedirs(comp, exist_ok=True)

    pares, alts, etapas = [], [], []
    alt_det, etapa_det, seqs, feicoes = [], [], [], []
    usadas = set(pontos)
    resumo, resumo_banco = {}, {}
    for cen in cenarios:
        cons = Consultor(rede, cen)
        cont, cont_banco = {}, {}
        for o in pontos:
            for d in pontos:
                if o == d:
                    continue  # CHECK do banco: origem <> destino
                r = cons.alternativas(o, d, criterio)
                st = STATUS_BANCO[r["status"]]
                cont[r["status"]] = cont.get(r["status"], 0) + 1
                cont_banco[st] = cont_banco.get(st, 0) + 1
                pares.append([cen, o, d, st, data_calculo, config.FONTE_CALCULO])
                for ordem, a in enumerate(r["alternativas"], 1):
                    chave = [cen, o, d, ordem]
                    alts.append(chave + [decimal_texto(a.tempo_s / 60, 1), decimal_texto(a.distancia_m / 1000, 2),
                                         a.baldeacoes])
                    k = ordem - 1
                    sob = max([x for q, x in enumerate(r["sobreposicao"][k]) if q != k], default=None)
                    alt_det.append(chave + [round(a.tempo_s), round(a.espera_s), round(a.bordo_s),
                                            round(a.distancia_m), a.embarques, len(a.paradas),
                                            round(a.distancia_m / r["linha_reta_m"], 2),
                                            "" if sob is None else round(sob, 3), ";".join(sorted(a.geradores))])
                    pos = 0
                    for seq, t in enumerate(a.trechos, 1):
                        etapas.append(chave + [seq, t.linha, t.embarque, t.desembarque])
                        usadas |= {t.embarque, t.desembarque}
                        etapa_det.append(chave + [seq, ";".join(t.linhas_equivalentes), round(t.espera_s),
                                                  round(t.bordo_s), round(t.distancia_m), t.partidas_linha,
                                                  t.partidas_combinadas])
                        for s in (t.paradas if seq == 1 else t.paradas[1:]):
                            pos += 1
                            p = rede["paradas"][s]
                            seqs.append(chave + [pos, s, seq, round(p["lat"], 6), round(p["lon"], 6)])
                    feicoes.append({"type": "Feature",
                                    "properties": dict(zip(CHAVE_ALTERNATIVA, chave),
                                                       linhas=" + ".join(t.linha for t in a.trechos),
                                                       nr_tempo_total_min=float(alts[-1][4]),
                                                       nr_distancia_km=float(alts[-1][5]),
                                                       qt_baldeacoes=a.baldeacoes),
                                    "geometry": {"type": "LineString", "coordinates": a.lonlat()}})
        resumo[cen], resumo_banco[cen] = cont, cont_banco
        log(f"{cen}: {cont_banco} (detalhe: {cont})")

    linhas_parada, origem_municipio = [], {}
    for cd in sorted(usadas, key=_ordem_codigo):
        p = rede["paradas"][cd]
        mun, origem = municipio(cd, p["nome"])
        origem_municipio[origem] = origem_municipio.get(origem, 0) + 1
        linhas_parada.append([cd, p["nome"], mun, round(p["lat"], 6), round(p["lon"], 6),
                              "S" if "terminal" in p["nome"].lower() else "N",
                              "S" if cd in pontos else "N", config.FONTE_GTFS])

    _csv(os.path.join(pasta, "ph_cenario.csv"), ["cd_cenario", "nm_cenario", "tp_dia", "nr_hora_inicio", "nr_hora_fim"],
         [[c, v["nome"], v["tp_dia"], int(v["inicio"][:2]), int(v["fim"][:2])] for c, v in config.CENARIOS.items()])
    _csv(os.path.join(pasta, "ph_parada.csv"),
         ["cd_parada_gtfs", "nm_parada", "nm_municipio", "nr_latitude", "nr_longitude", "fl_terminal",
          "fl_selecionavel", "nm_fonte"], linhas_parada)
    _csv(os.path.join(pasta, "ph_linha.csv"), ["cd_linha", "ds_itinerario", "tp_modal", "nm_fonte"],
         [[cd, v["nome"], "ONIBUS", config.FONTE_GTFS] for cd, v in sorted(rede["linhas"].items())])
    _csv(os.path.join(pasta, "ph_par_origem_destino.csv"),
         ["cd_cenario", "cd_parada_origem", "cd_parada_destino", "st_resultado", "dt_calculo", "nm_fonte"], pares)
    _csv(os.path.join(pasta, "ph_alternativa.csv"),
         CHAVE_ALTERNATIVA + ["nr_tempo_total_min", "nr_distancia_km", "qt_baldeacoes"], alts)
    _csv(os.path.join(pasta, "ph_etapa_trajeto.csv"),
         CHAVE_ALTERNATIVA + ["nr_sequencia", "cd_linha", "cd_parada_embarque", "cd_parada_desembarque"], etapas)

    _csv(os.path.join(comp, "alternativa_detalhe.csv"),
         CHAVE_ALTERNATIVA + ["tempo_total_s", "espera_s", "bordo_s", "distancia_m", "n_embarques", "n_paradas",
                              "indice_desvio", "sobreposicao_max", "geradores"], alt_det)
    _csv(os.path.join(comp, "etapa_detalhe.csv"),
         CHAVE_ALTERNATIVA + ["nr_sequencia", "linhas_equivalentes", "espera_s", "bordo_s", "distancia_m",
                              "partidas_linha_janela", "partidas_combinadas_janela"], etapa_det)
    _csv(os.path.join(comp, "sequencia_paradas.csv"),
         CHAVE_ALTERNATIVA + ["nr_posicao", "cd_parada", "nr_sequencia_etapa", "nr_latitude", "nr_longitude"], seqs)
    with open(os.path.join(comp, "alternativas.geojson"), "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": feicoes}, f, ensure_ascii=False)

    meta = {**rede["meta"],
            "data_calculo": data_calculo,
            "cenarios_exportados": {c: config.CENARIOS[c] for c in cenarios},
            "criterio_ordenacao": criterio,
            "pontos_selecionaveis": pontos,
            "status_por_cenario": resumo,
            "status_banco_por_cenario": resumo_banco,
            "fontes_banco": {"paradas_e_linhas": config.FONTE_GTFS, "pares": config.FONTE_CALCULO},
            "conversoes": {
                "modelo": "database/02_ddl.sql do repositório da equipe",
                "chaves": "id_* (IDENTITY) não exportados; FKs pela chave natural: cd_cenario, "
                          "cd_parada_gtfs, cd_linha, nm_fonte",
                "status": STATUS_BANCO,
                "tempo": "segundos / 60, 1 casa, meio para cima -> NUMBER(5,1)",
                "distancia": "metros / 1000, 2 casas, meio para cima -> NUMBER(6,2)",
                "etapa_linha": "cd_linha = linha do itinerário escolhido; linhas com o mesmo itinerário "
                               "no trecho ficam em complementar/etapa_detalhe.csv",
                "municipio": "do nome da parada no GTFS; senão config.MUNICIPIO_CONFERIDO; senão "
                             f"'{config.MUNICIPIO_NAO_INFORMADO}'",
                "municipio_origem": origem_municipio,
            },
            "parametros": {"MAX_ALTERNATIVAS": config.MAX_ALTERNATIVAS,
                           "MAX_BALDEACOES": config.MAX_BALDEACOES,
                           "MAX_INDICE_DESVIO": config.MAX_INDICE_DESVIO,
                           "LIMIAR_SOBREPOSICAO": config.LIMIAR_SOBREPOSICAO,
                           "RAIO_SOBREPOSICAO_M": config.RAIO_SOBREPOSICAO_M},
            "aviso_uso": "Tempos são programados/interpolados pela ARTESP (GTFS 2026), não tempo real. "
                         "Esperas são estimativas (headway/2). Baldeações só na mesma parada."}
    with open(os.path.join(pasta, "metadados.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    log(f"{len(pares)} pares, {len(alts)} alternativas, {len(etapas)} etapas, "
        f"{len(linhas_parada)} paradas -> {pasta}")
    return {"pares": len(pares), "alternativas": len(alts), "etapas": len(etapas),
            "paradas": len(linhas_parada), "status": resumo_banco}
