"""Extrai a rede piloto do GTFS da ARTESP para `dados/rede_piloto.json`.

O arquivo gerado contém apenas dados derivados do GTFS (paradas, padrões de
viagem, horários programados, traçados recortados) e metadados de auditoria.
Nenhum tempo, distância ou conexão é criado aqui: tudo vem de `stop_times.txt`
e `shapes.txt`.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import zipfile
from collections import defaultdict

import numpy as np
import pandas as pd

from . import config
from .alinhamento import alinhar_paradas, recortar
from .geo import para_lonlat, para_xy


ARQUIVOS_OBRIGATORIOS = ("feed_info.txt", "routes.txt", "trips.txt", "stops.txt",
                         "stop_times.txt", "shapes.txt")


def _sha256(caminho: str) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _ler(z: zipfile.ZipFile, nome: str, **kw) -> pd.DataFrame:
    with z.open(nome) as f:
        return pd.read_csv(io.TextIOWrapper(f, encoding="utf-8-sig"), **kw)


def _seg(hms: pd.Series) -> np.ndarray:
    p = hms.str.split(":", expand=True).astype(int)
    return (p[0] * 3600 + p[1] * 60 + p[2]).to_numpy()


def _no_recorte(lat, lon) -> np.ndarray:
    b = config.BBOX
    return (lat >= b["lat_min"]) & (lat <= b["lat_max"]) & (lon >= b["lon_min"]) & (lon <= b["lon_max"])


def extrair(gtfs_zip: str, saida_json: str, verbose: bool = True) -> dict:
    log = print if verbose else (lambda *a, **k: None)
    if not zipfile.is_zipfile(gtfs_zip):
        raise ValueError(f"{gtfs_zip} não existe ou não é um arquivo ZIP")
    with zipfile.ZipFile(gtfs_zip) as z:
        faltando = [n for n in ARQUIVOS_OBRIGATORIOS if n not in z.namelist()]
    if faltando:
        raise ValueError(f"o ZIP não parece um GTFS completo; faltam {faltando}")
    sha = _sha256(gtfs_zip)
    log(f"SHA-256 do ZIP: {sha}")
    ids = {"route_id": str, "trip_id": str, "stop_id": str, "shape_id": str,
           "service_id": str, "direction_id": str}
    with zipfile.ZipFile(gtfs_zip) as z:
        feed = _ler(z, "feed_info.txt", dtype=str)
        routes = _ler(z, "routes.txt", dtype=str)
        trips = _ler(z, "trips.txt", dtype=ids)
        stops = _ler(z, "stops.txt", dtype={"stop_id": str})
        st = _ler(z, "stop_times.txt", dtype={"trip_id": str, "stop_id": str,
                                               "arrival_time": str, "departure_time": str})
        log(f"stop_times: {len(st):,} registros")
        st = st.sort_values(["trip_id", "stop_sequence"], kind="stable")
        st["chegada"] = _seg(st.arrival_time)
        st["partida"] = _seg(st.departure_time)

        # Viagens que passam por alguma parada-âncora
        ancora = set(config.PARADAS_ANCORA)
        trips_anc = set(st.loc[st.stop_id.isin(ancora), "trip_id"])
        if not trips_anc:
            raise ValueError(f"nenhuma viagem passa pelas paradas-âncora {sorted(ancora)}; confira o GTFS")
        s = st[st.trip_id.isin(trips_anc)]
        seq = s.groupby("trip_id", sort=False).stop_id.agg(tuple)
        cheg = s.groupby("trip_id", sort=False).chegada.agg(tuple)
        part0 = s.groupby("trip_id", sort=False).partida.first()
        t = trips.set_index("trip_id").loc[seq.index].copy()
        t["seq"] = seq
        t["cheg"] = cheg
        t["part0"] = part0

        shape_ids = set(t.shape_id)
        shapes = _ler(z, "shapes.txt", dtype={"shape_id": str})
        shapes = shapes[shapes.shape_id.isin(shape_ids)].sort_values(["shape_id", "shape_pt_sequence"])

    S = stops.set_index("stop_id")
    shp = {k: g[["shape_pt_lon", "shape_pt_lat"]].to_numpy() for k, g in shapes.groupby("shape_id")}

    padroes = []
    avisos = []
    contagem_ids = defaultdict(int)
    for (rid, did, shid, sq), g in t.groupby(["route_id", "direction_id", "shape_id", "seq"], sort=True):
        if len(set(sq)) != len(sq):
            avisos.append(f"padrão {rid}/{did}/{shid} repete parada; ignorado")
            continue
        lat = S.loc[list(sq), "stop_lat"].to_numpy(float)
        lon = S.loc[list(sq), "stop_lon"].to_numpy(float)
        dentro = _no_recorte(lat, lon)
        if dentro.sum() < 2:
            continue
        # horários: deslocamento de cada parada em relação à 1ª (mediana entre viagens)
        mat = np.array(list(g.cheg), dtype=float)
        rel = mat - mat[:, :1]
        offset = np.median(rel, axis=0)
        variacao = float((rel.max(axis=0) - rel.min(axis=0)).max())
        hops = np.diff(mat, axis=1)
        uniforme = bool((hops.max(axis=1) - hops.min(axis=1) <= 2).all())
        partidas = {sid: sorted(int(x) for x in gg.part0) for sid, gg in g.groupby("service_id")}
        # traçado
        V = para_xy(shp[shid][:, 0], shp[shid][:, 1])
        P = para_xy(lon, lat)
        al = alinhar_paradas(P, V)
        idx_in = np.where(dentro)[0]
        p0, p1 = float(al["pos_m"][idx_in[0]]), float(al["pos_m"][idx_in[-1]])
        geom = recortar(V, al["cum_m"], p0, p1)
        geom_ll = para_lonlat(geom)
        if al["ajustes"]:
            avisos.append(f"padrão {rid}/{did}/{shid}: {al['ajustes']} posições ajustadas no alinhamento")
        longe = np.where(al["dist_m"] > config.ALERTA_PROJECAO_M)[0]
        for i in longe:
            if dentro[i]:
                avisos.append(f"padrão {rid}/{did}/{shid}: parada {sq[i]} a {al['dist_m'][i]:.0f} m do traçado")
        lacunas = int(((np.diff(idx_in)) > 1).sum())
        if lacunas:
            avisos.append(f"padrão {rid}/{did}/{shid}: sai e volta ao recorte {lacunas} vez(es)")
        pid = f"{rid}_{did}_{shid}"
        contagem_ids[pid] += 1
        if contagem_ids[pid] > 1:
            pid = f"{pid}_{contagem_ids[pid]}"
        padroes.append({
            "id": pid, "route_id": rid, "direction_id": did, "shape_id": shid,
            "headsign": str(g.trip_headsign.iloc[0]),
            "paradas": list(sq),
            "no_recorte": [bool(x) for x in dentro],
            "offset_s": [round(float(x), 1) for x in offset],
            "variacao_offset_s": variacao,
            "interpolacao_uniforme": uniforme,
            "duracao_s": round(float(offset[-1]), 1),
            "pos_m": [round(float(x), 1) for x in al["pos_m"]],
            "proj_m": [round(float(x), 1) for x in al["dist_m"]],
            "partidas": partidas,
            "geometria": {"inicio_m": round(p0, 1),
                          "coords": [[round(float(a), 6), round(float(b), 6)] for a, b in geom_ll]},
        })

    # Viagens duplicadas: mesma linha/sentido/serviço/partida em traçados diferentes
    dup = defaultdict(list)
    for p in padroes:
        for sid, lst in p["partidas"].items():
            dup[(p["route_id"], p["direction_id"], sid, tuple(lst))].append(p["id"])
    for k, v in dup.items():
        if len(v) > 1:
            avisos.append(f"linha {k[0]} sentido {k[1]} {k[2]}: padrões {v} têm a mesma lista de partidas "
                          f"({len(k[3])} viagens) - partidas contadas uma vez no grafo")

    usadas = sorted({x for p in padroes for x in p["paradas"]})
    paradas = {}
    for sid in usadas:
        r = S.loc[sid]
        paradas[sid] = {"nome": str(r.stop_name), "lat": float(r.stop_lat), "lon": float(r.stop_lon),
                        "no_recorte": bool(_no_recorte(np.array([r.stop_lat]), np.array([r.stop_lon]))[0])}
    linhas = {r.route_id: {"nome": r.route_long_name}
              for r in routes[routes.route_id.isin({p["route_id"] for p in padroes})].itertuples()}

    rede = {
        "meta": {
            "fonte": "ARTESP - GTFS (dadosabertos.artesp.sp.gov.br/dataset/gtfs)",
            "feed_version": str(feed.feed_version.iloc[0]),
            "vigencia": f"{feed.feed_start_date.iloc[0]}-{feed.feed_end_date.iloc[0]}",
            "sha256_zip": sha,
            "bbox": config.BBOX,
            "paradas_ancora": list(config.PARADAS_ANCORA),
            "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
            "n_padroes": len(padroes),
            "n_linhas": len(linhas),
            "n_paradas_no_recorte": sum(1 for p in paradas.values() if p["no_recorte"]),
            "todas_interpolacoes_uniformes": all(p["interpolacao_uniforme"] for p in padroes),
            "variacao_max_offset_s": max(p["variacao_offset_s"] for p in padroes),
            "avisos": avisos,
        },
        "linhas": linhas,
        "paradas": paradas,
        "padroes": padroes,
    }
    with open(saida_json, "w", encoding="utf-8") as f:
        json.dump(rede, f, ensure_ascii=False, separators=(",", ":"))
    log(f"{len(padroes)} padrões, {len(linhas)} linhas, {rede['meta']['n_paradas_no_recorte']} paradas no recorte")
    for a in avisos:
        log("AVISO:", a)
    return rede
