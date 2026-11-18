"""Floyd-Warshall: caminhos mínimos entre todos os pares (programação dinâmica).

Formulação em programação dinâmica:
    Estado      d(i, j, k) = menor custo de i até j usando só os vértices
                0..k-1 como intermediários.
    Decisão     passar ou não pelo vértice k-1.
    Transição   d(i, j, k) = min( d(i, j, k-1),                      não passa
                                  d(i, k-1, k-1) + d(k-1, j, k-1) )  passa
    Caso base   d(i, j, 0) = W[i][j]  (0 se i == j; infinito se não há aresta)
    Objetivo    d(i, j, V) para todos os pares (i, j).

O mesmo raciocínio aparece aqui em três versões, na sequência vista em aula:
  1. dist_recursiva       recursão pura: recalcula subproblemas, ~3^V chamadas
  2. floyd_warshall_memo  recursão + memoização (dicionário): V²·(V+1) estados,
                          memória Θ(V³)
  3. floyd_warshall       tabela de baixo para cima (bottom-up): Θ(V³) de tempo e
                          só Θ(V²) de memória, porque a camada k depende apenas
                          da camada k-1, e a linha e a coluna k não mudam nela.
                          Uma única matriz é atualizada no lugar. É a versão
                          usada pelo Pharos.
floyd_warshall_numpy é a versão 3 com o laço interno vetorizado; serve para
comparar desempenho. Os testes conferem que todas dão os mesmos resultados.

Reconstrução do caminho: NXT[i][j] guarda o próximo vértice depois de i no
melhor caminho até j. Quando k melhora o par (i, j), NXT[i][j] = NXT[i][k].
"""
from __future__ import annotations

import math

import numpy as np

INF = float("inf")
LIMITE_TOP_DOWN = 80   # versões 1 e 2 são didáticas: memória Θ(V³) e recursão de profundidade V


def _validar(W):
    """Confere se W é quadrada, sem pesos negativos ou NaN, e com diagonal 0."""
    n = len(W)
    for i, linha in enumerate(W):
        if len(linha) != n:
            raise ValueError("matriz de custos precisa ser quadrada")
        for j, w in enumerate(linha):
            if isinstance(w, float) and math.isnan(w):
                raise ValueError(f"peso NaN em ({i}, {j})")
            if w < 0:
                raise ValueError(f"peso negativo em ({i}, {j}); o modelo só usa custos >= 0")
            if i == j and w != 0:
                raise ValueError("a diagonal da matriz de custos deve ser 0")
    return n


# --------------------------------------------------------------------------
# Versão 3: tabela bottom-up (usada pelo Pharos)
# --------------------------------------------------------------------------
def floyd_warshall(W):
    """Tabela de menores custos entre todos os pares, em Python puro.

    W é uma lista de listas: W[i][j] é o custo da aresta i->j, INF quando não
    há aresta e 0 na diagonal. Devolve (D, NXT), sem alterar W:
      D[i][j]   menor custo de i até j (INF se não há caminho)
      NXT[i][j] próximo vértice depois de i no melhor caminho (-1 se não há)

    >>> W = [[0, 4, 1], [INF, 0, INF], [INF, 2, 0]]   # 0->1 custa 4, mas 0->2->1 custa 3
    >>> D, NXT = floyd_warshall(W)
    >>> D[0][1]
    3
    >>> reconstruir(NXT, 0, 1)
    [0, 2, 1]
    >>> D[1][0] == INF                                  # 1 não tem saída
    True
    """
    n = _validar(W)
    D = [linha[:] for linha in W]
    NXT = [[j if (i == j or W[i][j] < INF) else -1 for j in range(n)] for i in range(n)]
    for k in range(n):                      # camada k: libera o vértice k como intermediário
        # Só vale relaxar (i, j) se i alcança k e k alcança j: com um dos termos
        # infinito, a soma nunca melhora D[i][j]. A linha k não muda nesta
        # iteração, então os destinos alcançáveis a partir de k são listados uma vez.
        alvos = [(j, dkj) for j, dkj in enumerate(D[k]) if dkj < INF]
        for i in range(n):
            dik = D[i][k]
            if dik == INF or i == k:
                continue
            Di, Ni = D[i], NXT[i]
            nik = Ni[k]
            for j, dkj in alvos:
                c = dik + dkj               # decisão "passa por k"
                if c < Di[j]:               # melhor que "não passa por k"
                    Di[j] = c
                    Ni[j] = nik
    return D, NXT


def floyd_warshall_numpy(W):
    """Mesma recorrência da versão 3, vetorizada por iteração k (NumPy).

    Cada iteração calcula D[:, k] + D[k, :] para todos os pares de uma vez.
    O número de operações continua Θ(V³); só o laço interno sai do Python.
    """
    D = np.array(W, dtype=float)
    if D.ndim != 2 or D.shape[0] != D.shape[1]:
        raise ValueError("matriz de custos precisa ser quadrada")
    if np.isnan(D).any():
        raise ValueError("a matriz de custos tem NaN")
    if (D < 0).any():
        raise ValueError("peso negativo; o modelo só usa custos >= 0")
    if (np.diag(D) != 0).any():
        raise ValueError("a diagonal da matriz de custos deve ser 0")
    n = D.shape[0]
    NXT = np.where(np.isfinite(D), np.arange(n)[None, :], -1).astype(np.int64)
    for k in range(n):
        cand = D[:, k:k + 1] + D[k:k + 1, :]
        melhor = cand < D
        D = np.where(melhor, cand, D)
        NXT = np.where(melhor, NXT[:, k:k + 1], NXT)
    return D, NXT


def reconstruir(NXT, i: int, j: int):
    """Lista de vértices do caminho mínimo i->j, ou None se não houver caminho.

    >>> NXT = [[0, 2, 2], [-1, 1, -1], [-1, 1, 2]]
    >>> reconstruir(NXT, 0, 1)
    [0, 2, 1]
    >>> reconstruir(NXT, 1, 0) is None
    True
    """
    if NXT[i][j] == -1:
        return None
    caminho = [i]
    n = len(NXT)
    while i != j:
        i = int(NXT[i][j])
        caminho.append(i)
        if len(caminho) > n:
            raise RuntimeError("ciclo na matriz de sucessores (não deveria ocorrer com pesos >= 0)")
    return caminho


# --------------------------------------------------------------------------
# Versões 1 e 2: top-down (recursão e memoização), para mostrar de onde vem
# a tabela e conferir os resultados. O Pharos usa a versão 3.
# --------------------------------------------------------------------------
def dist_recursiva(W, i, j, k, medidor):
    """d(i, j, k) por recursão pura, sem cache.

    Cada chamada abre outras três, e por isso o número de chamadas cresce como
    3^k. `medidor` conta quantas vezes cada estado (i, j, k) foi calculado.

    >>> W = [[0, 4, 1], [INF, 0, INF], [INF, 2, 0]]
    >>> medidor = {}
    >>> dist_recursiva(W, 0, 1, 3, medidor)
    3
    >>> medidor[(0, 1, 0)] > 1                # o mesmo subproblema foi recalculado
    True
    """
    medidor[(i, j, k)] = medidor.get((i, j, k), 0) + 1
    if k == 0:                                # caso base: só a aresta direta
        return W[i][j]
    nao_passa = dist_recursiva(W, i, j, k - 1, medidor)
    passa = dist_recursiva(W, i, k - 1, k - 1, medidor) + dist_recursiva(W, k - 1, j, k - 1, medidor)
    return min(nao_passa, passa)


def dist_memo(W, i, j, k, memo, medidor):
    """d(i, j, k) por recursão com memoização: cada estado é calculado uma vez.

    >>> W = [[0, 4, 1], [INF, 0, INF], [INF, 2, 0]]
    >>> memo, medidor = {}, {}
    >>> dist_memo(W, 0, 1, 3, memo, medidor)
    3
    >>> max(medidor.values())                 # nenhum estado calculado duas vezes
    1
    """
    if (i, j, k) in memo:
        return memo[(i, j, k)]
    medidor[(i, j, k)] = medidor.get((i, j, k), 0) + 1
    if k == 0:
        resposta = W[i][j]
    else:
        nao_passa = dist_memo(W, i, j, k - 1, memo, medidor)
        passa = dist_memo(W, i, k - 1, k - 1, memo, medidor) + dist_memo(W, k - 1, j, k - 1, memo, medidor)
        resposta = min(nao_passa, passa)
    memo[(i, j, k)] = resposta
    return resposta


def floyd_warshall_memo(W):
    """Todos os pares pela versão top-down com memoização.

    Devolve (D, memo, medidor). O dicionário memo termina com V²·(V+1) estados
    (memória Θ(V³)), contra V² células da versão em tabela. Por isso a versão
    top-down é limitada a grafos pequenos (LIMITE_TOP_DOWN vértices).
    """
    n = _validar(W)
    if n > LIMITE_TOP_DOWN:
        raise ValueError(f"a versão com memoização é didática (até {LIMITE_TOP_DOWN} vértices); "
                         "use floyd_warshall para grafos maiores")
    memo, medidor = {}, {}
    D = [[dist_memo(W, i, j, n, memo, medidor) for j in range(n)] for i in range(n)]
    return D, memo, medidor
