"""Testes do alinhamento monotônico parada→traçado (tabulação)."""
import doctest
import itertools
import random
import unittest

import numpy as np

from pharos.alinhamento import alinhar_paradas, recortar


class TestAlinhamento(unittest.TestCase):
    def test_reta(self):
        tr = np.array([[0, 0], [100, 0], [200, 0]], dtype=float)
        p = np.array([[10, 5], [150, -3], [199, 1]], dtype=float)
        r = alinhar_paradas(p, tr)
        np.testing.assert_allclose(r["pos_m"], [10, 150, 199])
        np.testing.assert_allclose(r["dist_m"], [5, 3, 1])
        self.assertEqual(r["ajustes"], 0)

    def test_laco_respeita_ordem(self):
        # Traçado vai de (0,0) a (100,0), sobe e VOLTA passando a 10 m da ida.
        tr = np.array([[0, 0], [100, 0], [100, 10], [0, 10]], dtype=float)
        # 1ª parada no início da ida; 2ª parada perto do ponto (50, 4): mais
        # perto da IDA (4 m) do que da volta (6 m), mas vem depois de uma
        # parada que só existe na volta.
        p = np.array([[5, 0], [100, 5], [50, 4]], dtype=float)
        r = alinhar_paradas(p, tr)
        self.assertTrue(np.all(np.diff(r["pos_m"]) >= 0))
        self.assertAlmostEqual(r["pos_m"][2], 160)   # projetada na volta (110 + 50), não na ida
        # A projeção isolada (sem a restrição de ordem) teria escolhido a ida:
        from pharos.geo import distancia_ponto_segmentos
        d, _ = distancia_ponto_segmentos(p[2:3], tr[:-1], tr[1:])
        self.assertEqual(int(np.argmin(d[0])), 0)

    def test_segmento_de_tamanho_zero(self):
        tr = np.array([[0, 0], [0, 0], [100, 0]], dtype=float)
        r = alinhar_paradas(np.array([[0, 1], [60, 1]], dtype=float), tr)
        np.testing.assert_allclose(r["pos_m"], [0, 60])

    def test_recortar(self):
        tr = np.array([[0, 0], [100, 0], [100, 100]], dtype=float)
        cum = np.array([0, 100, 200], dtype=float)
        sub = recortar(tr, cum, 50, 150)
        np.testing.assert_allclose(sub, [[50, 0], [100, 0], [100, 50]])

    def test_tracado_invalido(self):
        with self.assertRaises(ValueError):
            alinhar_paradas(np.zeros((1, 2)), np.zeros((1, 2)))
        with self.assertRaises(ValueError):
            alinhar_paradas(np.zeros((0, 2)), np.zeros((3, 2)))

    def test_tabela_igual_forca_bruta(self):
        """A tabela acha o mesmo ótimo que testar todas as atribuições em ordem."""
        from pharos.geo import distancia_ponto_segmentos
        rnd = random.Random(42)
        for _ in range(60):
            n, m = rnd.randint(1, 4), rnd.randint(1, 6)
            tr = np.array([[rnd.uniform(0, 100), rnd.uniform(0, 100)] for _ in range(m + 1)])
            p = np.array([[rnd.uniform(0, 100), rnd.uniform(0, 100)] for _ in range(n)])
            custo, _ = distancia_ponto_segmentos(p, tr[:-1], tr[1:])
            # todas as escolhas de segmentos em ordem não decrescente
            bruta = min(sum(custo[i][s] for i, s in enumerate(comb))
                        for comb in itertools.combinations_with_replacement(range(m), n))
            r = alinhar_paradas(p, tr)
            self.assertAlmostEqual(r["custo_total"], bruta, places=9)
            self.assertTrue(all(a <= b for a, b in zip(r["seg"], r["seg"][1:])))


def load_tests(loader, tests, ignore):
    import pharos.alinhamento
    tests.addTests(doctest.DocTestSuite(pharos.alinhamento))
    return tests


if __name__ == "__main__":
    unittest.main()
