"""Análise prática de eficiência do Floyd-Warshall na rede piloto.

Compara, sobre a MESMA matriz de custos:
  * Floyd-Warshall em Python puro  - Θ(V³) tempo, Θ(V²) memória
  * Floyd-Warshall vetorizado      - mesma recorrência, laço interno em NumPy
  * Dijkstra a partir de cada vértice (heap binário, heapq) -
    O(V · (V + E) · log V) tempo, O(V + E) memória por origem
e confere que as três abordagens dão exatamente as mesmas distâncias.

Todas as funções são puras: recebem a matriz e devolvem resultados, sem
imprimir nada. A apresentação fica em main.py.
"""
from __future__ import annotations

import heapq
import math
import time

import numpy as np

from .floyd_warshall import (INF, LIMITE_TOP_DOWN, dist_recursiva, floyd_warshall,
                             floyd_warshall_memo, floyd_warshall_numpy)


def lista_adjacencia(W):
    """Converte a matriz de custos em listas de adjacência [(vizinho, peso), ...]."""
    n = len(W)
    return [[(j, w) for j, w in enumerate(W[i]) if j != i and w < INF] for i in range(n)]


def dijkstra(adj, origem: int):
    """Menores custos a partir de `origem` com fila de prioridade (heapq)."""
    dist = [INF] * len(adj)
    dist[origem] = 0.0
    fila = [(0.0, origem)]
    while fila:
        d, u = heapq.heappop(fila)
        if d > dist[u]:
            continue                      # entrada antiga da fila
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(fila, (nd, v))
    return dist


def dijkstra_todos_pares(W):
    adj = lista_adjacencia(W)
    return [dijkstra(adj, s) for s in range(len(W))]


def cronometrar(funcao, *args, repeticoes: int = 3):
    """Menor tempo (s) entre `repeticoes` execuções e o resultado da última."""
    melhor, resultado = INF, None
    for _ in range(max(1, repeticoes)):
        t0 = time.perf_counter()
        resultado = funcao(*args)
        melhor = min(melhor, time.perf_counter() - t0)
    return melhor, resultado


def _iguais(a, b) -> bool:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape or not np.array_equal(np.isinf(a), np.isinf(b)):
        return False
    fin = np.isfinite(a)
    return bool(np.allclose(a[fin], b[fin], rtol=1e-12, atol=1e-9))


def contar_arestas(W) -> int:
    return sum(1 for i, linha in enumerate(W) for j, w in enumerate(linha) if i != j and w < INF)


def comparar(W, repeticoes: int = 3) -> dict:
    """Mede as três abordagens na matriz W e confere se os resultados coincidem."""
    n, e = len(W), contar_arestas(W)
    t_py, (d_py, _) = cronometrar(floyd_warshall, W, repeticoes=repeticoes)
    t_np, (d_np, _) = cronometrar(floyd_warshall_numpy, W, repeticoes=repeticoes)
    t_dj, d_dj = cronometrar(dijkstra_todos_pares, W, repeticoes=repeticoes)
    return {
        "vertices": n, "arestas": e,
        "fw_python_s": t_py, "fw_numpy_s": t_np, "dijkstra_todos_s": t_dj,
        "operacoes_fw": n ** 3,
        "operacoes_dijkstra": int(n * (n + e) * math.log2(max(n, 2))),
        "python_igual_numpy": _iguais(d_py, d_np),
        "python_igual_dijkstra": _iguais(d_py, d_dj),
        "pares_alcancaveis": int(np.isfinite(np.asarray(d_py, dtype=float)).sum() - n),
    }


def crescimento(W, tamanhos, repeticoes: int = 3) -> list:
    """Tempo do Floyd-Warshall em subgrafos induzidos pelos k primeiros vértices.

    Se o algoritmo é Θ(V³), o tempo dividido por k³ fica aproximadamente
    constante (na versão NumPy, que não pula linhas inalcançáveis, isso é
    mais visível).
    """
    linhas = []
    for k in tamanhos:
        k = min(k, len(W))
        Wk = [linha[:k] for linha in W[:k]]
        t_py, _ = cronometrar(floyd_warshall, Wk, repeticoes=repeticoes)
        t_np, _ = cronometrar(floyd_warshall_numpy, Wk, repeticoes=repeticoes)
        linhas.append({"k": k, "fw_python_s": t_py, "fw_numpy_s": t_np,
                       "ns_por_k3_python": t_py / k ** 3 * 1e9, "ns_por_k3_numpy": t_np / k ** 3 * 1e9})
    return linhas


def versoes_do_curso(W, tamanhos_recursao=(4, 6, 8), tamanhos_memo=(30, 60)):
    """Recursão pura x memoização x tabela, nos subgrafos com os k primeiros vértices.

    Mostra na prática a sequência da apostila: a recursão recalcula subproblemas
    (chamadas crescem como 3^k), a memoização calcula cada estado uma vez, mas
    guarda V²·(V+1) estados, e a tabela usa só V² células. Confere se as três
    dão as mesmas distâncias.
    """
    linhas = []
    for k in sorted(set(tamanhos_recursao) | set(tamanhos_memo)):
        k = min(k, len(W))
        Wk = [linha[:k] for linha in W[:k]]
        t_tab, (d_tab, _) = cronometrar(floyd_warshall, Wk, repeticoes=1)
        lin = {"k": k, "tabela_s": t_tab, "tabela_celulas": k * k}
        if k <= LIMITE_TOP_DOWN:
            t_memo, (d_memo, memo, _) = cronometrar(floyd_warshall_memo, Wk, repeticoes=1)
            lin.update({"memo_s": t_memo, "memo_estados": len(memo), "memo_igual": d_memo == d_tab})
        if k in tamanhos_recursao:
            medidor = {}
            t0 = time.perf_counter()
            d_rec = [[dist_recursiva(Wk, i, j, k, medidor) for j in range(k)] for i in range(k)]
            lin.update({"recursao_s": time.perf_counter() - t0,
                        "recursao_chamadas": sum(medidor.values()),
                        "recursao_igual": d_rec == d_tab})
        linhas.append(lin)
    return linhas


def projecao_gtfs_completo(n: int = 25105) -> dict:
    """Ordem de grandeza para o GTFS inteiro da ARTESP (25.105 paradas)."""
    return {"vertices": n, "relaxacoes": n ** 3, "bytes_por_matriz": n * n * 8}
