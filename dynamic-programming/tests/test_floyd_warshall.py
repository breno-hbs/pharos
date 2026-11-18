"""Testes do algoritmo em grafos pequenos (resultados conferidos à mão) e
comparação com um oráculo independente (Dijkstra com heapq e listas de
adjacência, em pharos/desempenho.py)."""
import doctest
import random
import unittest

import numpy as np

from pharos.desempenho import comparar, dijkstra_todos_pares, versoes_do_curso
from pharos import floyd_warshall as fw_mod
from pharos.floyd_warshall import (INF, dist_recursiva, floyd_warshall, floyd_warshall_memo,
                                    floyd_warshall_numpy, reconstruir)


def grafo_aleatorio(n, densidade, semente):
    rnd = random.Random(semente)
    W = [[0.0 if i == j else INF for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and rnd.random() < densidade:
                W[i][j] = float(rnd.randint(1, 50))
    return W


# Grafo dirigido de 5 vértices (A..E) usado nos testes à mão:
#   A->B 4, A->C 1, C->B 2, B->D 1, C->D 5, D->E 3.  E não tem saída.
A, B, C, D, E = range(5)
W5 = [[0, 4, 1, INF, INF],
      [INF, 0, INF, 1, INF],
      [INF, 2, 0, 5, INF],
      [INF, INF, INF, 0, 3],
      [INF, INF, INF, INF, 0]]


class TestPequeno(unittest.TestCase):
    def setUp(self):
        self.D, self.N = floyd_warshall(W5)

    def test_distancias_conferidas_a_mao(self):
        # A->B: direto 4, via C 1+2 = 3  |  A->D: A-C-B-D = 1+2+1 = 4  |  A->E = 4+3 = 7
        self.assertEqual(self.D[A][B], 3)
        self.assertEqual(self.D[A][D], 4)
        self.assertEqual(self.D[A][E], 7)
        self.assertEqual(self.D[C][E], 6)          # C-B-D-E = 2+1+3

    def test_reconstrucao(self):
        self.assertEqual(reconstruir(self.N, A, E), [A, C, B, D, E])
        self.assertEqual(reconstruir(self.N, C, D), [C, B, D])   # 3 < 5 da aresta direta

    def test_sem_caminho(self):
        self.assertEqual(self.D[E][A], INF)
        self.assertIsNone(reconstruir(self.N, E, A))
        self.assertIsNone(reconstruir(self.N, B, C))              # só existe C->B

    def test_grafo_dirigido(self):
        self.assertLess(self.D[C][B], INF)
        self.assertEqual(self.D[B][C], INF)

    def test_origem_igual_destino(self):
        for v in range(5):
            self.assertEqual(self.D[v][v], 0)
            self.assertEqual(reconstruir(self.N, v, v), [v])

    def test_custo_do_caminho_bate_com_tabela(self):
        for i in range(5):
            for j in range(5):
                cam = reconstruir(self.N, i, j)
                if cam:
                    self.assertEqual(sum(W5[a][b] for a, b in zip(cam, cam[1:])), self.D[i][j])

    def test_entrada_invalida(self):
        with self.assertRaises(ValueError):
            floyd_warshall([[0, -1], [INF, 0]])
        with self.assertRaises(ValueError):
            floyd_warshall([[1, 2], [3, 0]])
        with self.assertRaises(ValueError):
            floyd_warshall([[0, 1, 2], [0, 1]])
        with self.assertRaises(ValueError):
            floyd_warshall_numpy([[0, -1], [INF, 0]])

    def test_vazio_e_unitario(self):
        self.assertEqual(floyd_warshall([]), ([], []))
        D, N = floyd_warshall([[0]])
        self.assertEqual((D, N), ([[0]], [[0]]))


class TestAleatorio(unittest.TestCase):
    def test_python_igual_numpy_e_dijkstra(self):
        for semente in range(40):
            n = 1 + semente % 25
            W = grafo_aleatorio(n, densidade=(semente % 5 + 1) / 10, semente=semente)
            D1, N1 = floyd_warshall(W)
            D2, N2 = floyd_warshall_numpy(W)
            np.testing.assert_array_equal(np.array(D1, dtype=float), D2)
            np.testing.assert_array_equal(np.array(N1), N2)
            DJ = dijkstra_todos_pares(W)
            for s in range(n):
                self.assertEqual(D1[s], DJ[s], f"semente {semente}, origem {s}")
                for t in range(n):
                    cam = reconstruir(N1, s, t)
                    if D1[s][t] == INF:
                        self.assertIsNone(cam)
                    else:
                        self.assertEqual(cam[0], s)
                        self.assertEqual(cam[-1], t)
                        self.assertAlmostEqual(sum(W[a][b] for a, b in zip(cam, cam[1:])), D1[s][t])


    def test_comparar_desempenho(self):
        r = comparar(grafo_aleatorio(30, 0.2, 7), repeticoes=1)
        self.assertTrue(r["python_igual_numpy"])
        self.assertTrue(r["python_igual_dijkstra"])
        self.assertEqual(r["operacoes_fw"], 30 ** 3)
        for chave in ("fw_python_s", "fw_numpy_s", "dijkstra_todos_s"):
            self.assertGreaterEqual(r[chave], 0.0)


class TestVersoesDoCurso(unittest.TestCase):
    """Recursão, memoização e tabela: a mesma recorrência dá o mesmo resultado."""

    def test_memo_igual_tabela(self):
        D_tab, _ = floyd_warshall(W5)
        D_memo, memo, medidor = floyd_warshall_memo(W5)
        self.assertEqual(D_memo, D_tab)
        self.assertEqual(len(memo), 5 * 5 * (5 + 1))           # V²·(V+1) estados
        self.assertEqual(max(medidor.values()), 1)              # cada estado uma vez
        for semente in range(25):
            n = 1 + semente % 12
            W = grafo_aleatorio(n, (semente % 4 + 1) / 8, semente)
            self.assertEqual(floyd_warshall_memo(W)[0], floyd_warshall(W)[0], f"semente {semente}")

    def test_recursao_pura_recalcula(self):
        n = 5
        medidor = {}
        resposta = [[dist_recursiva(W5, i, j, n, medidor) for j in range(n)] for i in range(n)]
        self.assertEqual(resposta, floyd_warshall(W5)[0])
        chamadas = sum(medidor.values())
        self.assertEqual(chamadas, n * n * (3 ** (n + 1) - 1) // 2)   # cresce como 3^V
        self.assertGreater(chamadas, len(medidor))                     # houve recálculo

    def test_medicao_das_versoes(self):
        linhas = versoes_do_curso(grafo_aleatorio(12, 0.3, 3), tamanhos_recursao=(4, 6), tamanhos_memo=(10,))
        self.assertEqual([lin["k"] for lin in linhas], [4, 6, 10])
        for lin in linhas:
            self.assertTrue(lin["memo_igual"])
            self.assertEqual(lin["memo_estados"], lin["k"] ** 2 * (lin["k"] + 1))
        self.assertEqual(linhas[1]["recursao_chamadas"], 36 * (3 ** 7 - 1) // 2)
        self.assertTrue(linhas[1]["recursao_igual"])

    def test_limite_e_nan(self):
        grande = [[0.0 if i == j else INF for j in range(fw_mod.LIMITE_TOP_DOWN + 1)]
                  for i in range(fw_mod.LIMITE_TOP_DOWN + 1)]
        with self.assertRaises(ValueError):
            floyd_warshall_memo(grande)
        with self.assertRaises(ValueError):
            floyd_warshall([[0, float("nan")], [1, 0]])
        with self.assertRaises(ValueError):
            floyd_warshall_numpy([[0, float("nan")], [1, 0]])


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(fw_mod))
    return tests


if __name__ == "__main__":
    unittest.main()
