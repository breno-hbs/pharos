"""Alinhamento monotônico das paradas ao traçado (tabulação).

Problema: o GTFS da ARTESP não traz `shape_dist_traveled`. Para medir a
distância percorrida entre duas paradas, cada parada precisa ser projetada no
traçado (`shapes.txt`) respeitando a ordem da viagem. Projetar cada parada no
segmento mais próximo, isoladamente, falha quando o traçado passa duas vezes
perto do mesmo ponto (laços em terminais, ida e volta pela mesma via).

Formulação em programação dinâmica (tabulação, como no problema 5.2 da apostila):
    Estado      M[i][j] = menor soma de distâncias para projetar as paradas
                0..i, com a parada i no segmento j
    Decisão     em qual segmento j' <= j ficou a parada anterior
    Transição   M[i][j] = custo[i][j] + min( M[i-1][0..j] )
    Caso base   M[0][j] = custo[0][j]
    Objetivo    min_j M[n-1][j], com o caminho reconstruído pela tabela `escolha`
O mínimo de M[i-1][0..j] é carregado enquanto j avança, então cada célula custa
O(1): tempo e memória O(n·m) (n paradas, m segmentos do traçado).
"""
from __future__ import annotations

import numpy as np

from .geo import distancia_ponto_segmentos

INF = float("inf")


def alinhar_paradas(paradas_xy: np.ndarray, tracado_xy: np.ndarray):
    """Projeta paradas (n×2) no traçado (m+1 vértices) em ordem não decrescente.

    Retorna dict com:
      seg      índice do segmento escolhido para cada parada
      pos_m    posição ao longo do traçado (m), não decrescente
      dist_m   distância da parada ao ponto projetado
      ajustes  quantas posições precisaram ser corrigidas para manter a ordem
               (duas paradas no mesmo segmento com projeção invertida)
      custo_total  valor ótimo da tabela (soma das distâncias de projeção)

    >>> tracado = [[0, 0], [100, 0], [100, 10], [0, 10]]   # vai, sobe e volta
    >>> paradas = [[5, 0], [100, 5], [50, 4]]               # a 3ª está mais perto da ida
    >>> alinhar_paradas(paradas, tracado)["pos_m"].round(1).tolist()
    [5.0, 105.0, 160.0]
    """
    P = np.asarray(paradas_xy, dtype=float)
    V = np.asarray(tracado_xy, dtype=float)
    if len(V) < 2:
        raise ValueError("traçado com menos de dois vértices")
    if len(P) == 0:
        raise ValueError("nenhuma parada para alinhar")
    A, B = V[:-1], V[1:]
    # Geometria (NumPy): custo[i][j] = distância da parada i ao segmento j
    custo_np, t = distancia_ponto_segmentos(P, A, B)
    custo = custo_np.tolist()
    n, m = len(custo), len(custo[0])

    # Tabela M (n x m) e escolha[i][j] = segmento usado pela parada i-1
    M = [custo[0][:]]                       # caso base: primeira parada
    escolha = [[0] * m]
    for i in range(1, n):
        anterior = M[i - 1]
        linha, esc = [0.0] * m, [0] * m
        melhor, melhor_j = INF, 0           # min(M[i-1][0..j]) e onde ele está
        for j in range(m):
            if anterior[j] < melhor:
                melhor, melhor_j = anterior[j], j
            linha[j] = custo[i][j] + melhor
            esc[j] = melhor_j
        M.append(linha)
        escolha.append(esc)

    # Reconstrução: da última parada para a primeira
    seg = [0] * n
    seg[-1] = min(range(m), key=lambda j: M[-1][j])
    for i in range(n - 1, 0, -1):
        seg[i - 1] = escolha[i][seg[i]]
    seg = np.array(seg, dtype=np.int64)

    seglen = np.hypot(*(B - A).T)
    cum = np.concatenate([[0.0], np.cumsum(seglen)])
    ti = t[np.arange(n), seg]
    pos = cum[seg] + ti * seglen[seg]
    ajustes = 0
    for i in range(1, n):
        if pos[i] < pos[i - 1]:
            pos[i] = pos[i - 1]
            ajustes += 1
    dist = custo_np[np.arange(n), seg]
    return {"seg": seg, "pos_m": pos, "dist_m": dist, "ajustes": ajustes,
            "cum_m": cum, "custo_total": min(M[-1])}


def recortar(tracado_xy: np.ndarray, cum: np.ndarray, p0: float, p1: float) -> np.ndarray:
    """Sub-polilinha do traçado entre as posições p0 <= p1 (m)."""
    V = np.asarray(tracado_xy, dtype=float)
    if p1 < p0:
        raise ValueError("p1 < p0")
    x0 = np.interp(p0, cum, V[:, 0]); y0 = np.interp(p0, cum, V[:, 1])
    x1 = np.interp(p1, cum, V[:, 0]); y1 = np.interp(p1, cum, V[:, 1])
    meio = V[(cum > p0) & (cum < p1)]
    return np.vstack([[x0, y0], meio, [x1, y1]])
