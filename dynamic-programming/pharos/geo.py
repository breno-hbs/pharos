"""Funções geométricas em plano local (metros).

Usa fatores métricos locais do elipsoide WGS84 na latitude de referência.
No recorte do piloto (~8 km) o erro dessa aproximação é desprezível perto da
precisão das coordenadas da fonte.
"""
from __future__ import annotations

import math

import numpy as np

from .config import LAT_REF


def fatores_metricos(lat_ref: float = LAT_REF) -> tuple[float, float]:
    """Metros por grau de longitude e de latitude (WGS84) na latitude dada."""
    phi = math.radians(lat_ref)
    m_lat = 111132.92 - 559.82 * math.cos(2 * phi) + 1.175 * math.cos(4 * phi)
    m_lon = 111412.84 * math.cos(phi) - 93.5 * math.cos(3 * phi)
    return m_lon, m_lat


KX, KY = fatores_metricos()
LON0, LAT0 = -46.78, LAT_REF


def para_xy(lon, lat) -> np.ndarray:
    """Converte lon/lat (graus) para x/y em metros no plano local."""
    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)
    return np.stack([(lon - LON0) * KX, (lat - LAT0) * KY], axis=-1)


def para_lonlat(xy) -> np.ndarray:
    xy = np.asarray(xy, dtype=float)
    return np.stack([xy[..., 0] / KX + LON0, xy[..., 1] / KY + LAT0], axis=-1)


def comprimento(xy: np.ndarray) -> float:
    if len(xy) < 2:
        return 0.0
    return float(np.hypot(*np.diff(xy, axis=0).T).sum())


def distancia_ponto_segmentos(p: np.ndarray, a: np.ndarray, b: np.ndarray):
    """Distância de cada ponto p (n×2) a cada segmento a→b (m×2).

    Retorna (dist n×m, t n×m), em que t ∈ [0, 1] é a posição da projeção no
    segmento. Segmentos de comprimento zero recebem t = 0.
    """
    ab = b - a                                   # m×2
    L2 = (ab ** 2).sum(axis=1)                   # m
    ap = p[:, None, :] - a[None, :, :]           # n×m×2
    with np.errstate(invalid="ignore", divide="ignore"):
        t = (ap * ab[None]).sum(axis=2) / L2[None]
    t = np.where(L2[None] > 0, np.clip(t, 0.0, 1.0), 0.0)
    proj = a[None] + t[..., None] * ab[None]
    d = np.hypot(*(p[:, None, :] - proj).transpose(2, 0, 1))
    return d, t


def amostrar(xy: np.ndarray, passo: float) -> np.ndarray:
    """Pontos a cada `passo` metros ao longo da polilinha (inclui extremos)."""
    if len(xy) < 2:
        return xy.copy()
    seg = np.hypot(*np.diff(xy, axis=0).T)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = cum[-1]
    if total == 0:
        return xy[:1].copy()
    s = np.append(np.arange(0.0, total, passo), total)
    x = np.interp(s, cum, xy[:, 0])
    y = np.interp(s, cum, xy[:, 1])
    return np.stack([x, y], axis=1)


def fracao_proxima(a_xy: np.ndarray, b_xy: np.ndarray, raio: float, passo: float) -> float:
    """Fração da extensão de A que fica a até `raio` metros da polilinha B."""
    if len(a_xy) < 2 or len(b_xy) < 2:
        return 0.0
    pts = amostrar(a_xy, passo)
    d, _ = distancia_ponto_segmentos(pts, b_xy[:-1], b_xy[1:])
    return float((d.min(axis=1) <= raio).mean())
