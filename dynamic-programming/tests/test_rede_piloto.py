"""Testes sobre a rede piloto real (dados/rede_piloto.json, extraída do GTFS).

Os valores esperados foram conferidos no GTFS da ARTESP versão 20261007
(SHA-256 f3fdca95...d45a). Se o arquivo for regenerado com outro GTFS, os testes
de identificadores e contagens indicam o que mudou.
"""
import os
import unittest

import numpy as np

from pharos import config
from pharos.alternativas import Consultor
from pharos.floyd_warshall import floyd_warshall, floyd_warshall_numpy, reconstruir
from pharos.grafo import carregar_rede

REDE = os.path.join(os.path.dirname(__file__), "..", "dados", "rede_piloto.json")
SHA = "f3fdca9599e512e191f1bb78cebcafab1bac8a458fbdd5c5e71cc2d10d97d45a"


def linhas_da(alt):
    return [set(t.linhas_equivalentes) for t in alt.trechos]


@unittest.skipUnless(os.path.exists(REDE), "rede piloto não gerada")
class TestRedePiloto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rede = carregar_rede(REDE)
        cls.c = Consultor(cls.rede, "UTIL_MANHA")

    # ---------------------------------------------------------- dados
    def test_procedencia(self):
        m = self.rede["meta"]
        self.assertEqual(m["sha256_zip"], SHA)
        self.assertEqual(m["feed_version"], "20261007")
        self.assertTrue(m["todas_interpolacoes_uniformes"])
        self.assertEqual(m["n_linhas"], 15)

    def test_001_e_002_mesmas_paradas_no_corredor(self):
        p = {x["id"]: x["paradas"] for x in self.rede["padroes"]}
        esperado = ["393", "394", "12643", "396", "397", "398", "399", "400", "401", "402", "403", "404", "405"]
        for pid in ("001_0_6509", "002_0_338"):
            seq = p[pid]
            i = seq.index("393")
            self.assertEqual(seq[i:i + 13], esperado, pid)

    # ------------------------------------------------- alternativas
    def test_corredor_001_002_e_uma_alternativa_so(self):
        r = self.c.alternativas("396", "405")
        self.assertEqual(r["status"], "TRAJETO_UNICO")
        self.assertEqual(len(r["alternativas"]), 1)
        eq = r["alternativas"][0].trechos[0].linhas_equivalentes
        self.assertIn("001", eq)
        self.assertIn("002", eq)

    def test_embu_metro_duas_alternativas_distintas(self):
        r = self.c.alternativas("13211", "407")
        self.assertEqual(r["status"], "ALTERNATIVAS_DISTINTAS")
        a1, a2 = r["alternativas"][:2]
        self.assertEqual(linhas_da(a1), [{"551", "551BI1"}])     # via Av. Carlos Lacerda
        self.assertEqual(linhas_da(a2), [{"193"}])               # via Estrada de Itapecerica
        self.assertEqual((a1.baldeacoes, a2.baldeacoes), (0, 0))
        self.assertLess(r["sobreposicao"][0][1], 0.30)
        self.assertIn("12643", a2.paradas)                       # 193 usa o corredor piloto
        self.assertNotIn("12643", a1.paradas)
        self.assertIn("33608", a1.paradas)                       # 551 usa a Av. Carlos Lacerda
        self.assertAlmostEqual(a1.distancia_m, 6000, delta=50)
        self.assertAlmostEqual(a2.distancia_m, 8972, delta=50)

    def test_metro_embu_volta(self):
        r = self.c.alternativas("407", "13466")
        self.assertEqual(r["status"], "ALTERNATIVAS_DISTINTAS")
        self.assertEqual([linhas_da(a) for a in r["alternativas"]], [[{"551"}], [{"193"}]])

    def test_mboi_mirim_metro(self):
        r = self.c.alternativas("32960", "407")
        self.assertEqual(r["status"], "ALTERNATIVAS_DISTINTAS")
        conj = [linhas_da(a)[0] for a in r["alternativas"]]
        self.assertIn({"237"}, conj)
        self.assertIn({"513", "558", "563", "844"}, conj)
        self.assertLess(r["sobreposicao"][0][1], config.LIMIAR_SOBREPOSICAO)

    def test_baldeacao_no_terminal(self):
        r = self.c.alternativas("405", "2201")
        self.assertEqual(r["status"], "ALTERNATIVAS_DISTINTAS")
        for a in r["alternativas"]:
            self.assertEqual(a.baldeacoes, 1)
            self.assertEqual(a.pontos_baldeacao, ["407"])
        segundas = [set(a.trechos[1].linhas_equivalentes) for a in r["alternativas"]]
        self.assertIn({"237"}, segundas)
        self.assertIn({"513", "558", "563", "844"}, segundas)
        # a conexão existe no quadro de horários de dia útil
        s = self.c.simular(r["alternativas"][0], "07:00")
        self.assertTrue(s["viavel"])
        self.assertEqual(len(s["passos"]), 2)

    def test_trechos_existem_no_gtfs(self):
        """Cada trecho tem que ser uma subsequência contígua de um padrão real."""
        seqs = [x["paradas"] for x in self.rede["padroes"]]
        for o, d in [("13211", "407"), ("407", "13466"), ("32960", "407"), ("405", "2201")]:
            for a in self.c.alternativas(o, d)["alternativas"]:
                for t in a.trechos:
                    achou = any(t.paradas == s[s.index(t.embarque):s.index(t.embarque) + len(t.paradas)]
                                for s in seqs if t.embarque in s)
                    self.assertTrue(achou, (o, d, t.linha))

    # ------------------------------------------------ casos sem solução
    def test_sem_trajeto_no_piloto(self):
        # 393 só recebe ônibus vindos de Itapecerica, fora do recorte
        self.assertEqual(self.c.alternativas("407", "393")["status"], "SEM_TRAJETO")
        self.assertEqual(self.c.alternativas("407", "32960")["status"], "SEM_TRAJETO")

    def test_atravessar_a_rua_nao_e_trajeto(self):
        # 32960 e 2201 ficam em lados opostos da M'Boi Mirim (~37 m): o único
        # caminho de ônibus é ir ao terminal e voltar (~9 km)
        r = self.c.alternativas("32960", "2201")
        self.assertEqual(r["status"], "SEM_TRAJETO_RAZOAVEL")
        self.assertTrue(all(f["indice_desvio"] > 100 for f in r["filtradas"]))

    def test_parada_inexistente_e_origem_igual_destino(self):
        with self.assertRaises(KeyError):
            self.c.alternativas("99999", "407")
        self.assertEqual(self.c.alternativas("407", "407")["status"], "ORIGEM_IGUAL_DESTINO")

    def test_sem_partida_depois_do_ultimo_onibus(self):
        r = self.c.alternativas("13211", "407")
        a193 = r["alternativas"][1]
        s = self.c.simular(a193, "23:59")
        self.assertFalse(s["viavel"])

    # ------------------------------------------------------- cenários
    def test_cenario_muda_linhas_disponiveis(self):
        # 551BI1 sentido 0 só opera de manhã (05h00-08h10 na origem da linha)
        tarde = Consultor(self.rede, "UTIL_TARDE")
        r = tarde.alternativas("13211", "407")
        self.assertEqual(linhas_da(r["alternativas"][0]), [{"551"}])

    # ---------------------------------------------- critérios de custo
    def test_criterios_escolhem_caminhos_diferentes(self):
        A = self.c.g.arestas
        t = self.c.melhor_caminho("1325", "407", "tempo")
        d = self.c.melhor_caminho("1325", "407", "distancia")
        self.assertEqual([A[x].linha for x in t], ["513"])
        self.assertEqual([A[x].linha for x in d], ["237"])
        self.assertLess(sum(A[x].distancia_m for x in d), sum(A[x].distancia_m for x in t))
        self.assertLessEqual(sum(A[x].peso("tempo") for x in t), sum(A[x].peso("tempo") for x in d))

    # ---------------------------------------------- propriedades do FW
    def test_otimos_sao_validos(self):
        """Nenhum ótimo de nenhum critério tem baldeação inútil ou laço."""
        for c in config.CRITERIOS:
            ruins = 0
            for o in self.c.g.vertices:
                for dd in self.c.g.vertices:
                    if o != dd:
                        cam = self.c.melhor_caminho(o, dd, c)
                        if cam is not None and not self.c.valido(cam):
                            ruins += 1
            self.assertEqual(ruins, 0, c)

    def test_python_igual_numpy_na_rede(self):
        W, _ = self.c.g.matriz("tempo")
        D1, N1 = floyd_warshall(W)
        D2, N2 = floyd_warshall_numpy(W)
        np.testing.assert_array_equal(np.array(D1), D2)
        np.testing.assert_array_equal(np.array(N1), N2)

    def test_custo_reconstruido_igual_tabela(self):
        for c in config.CRITERIOS:
            W, D, N = self.c.W[c], self.c.D[c], self.c.NXT[c]
            n = len(W)
            for i in range(0, n, 7):
                for j in range(0, n, 5):
                    cam = reconstruir(N, i, j)
                    if cam is None:
                        self.assertTrue(np.isinf(D[i, j]))
                    else:
                        self.assertAlmostEqual(sum(W[a][b] for a, b in zip(cam, cam[1:])), D[i, j], places=6)


class TestMediaDosSaltos(unittest.TestCase):
    """A média de cada salto canônico não pode depender da ordem da soma nem da
    versão do NumPy: um último bit diferente desempata de outro jeito dois
    caminhos de mesmo custo (ex.: baldear em 1443 ou em 1444)."""

    def test_soma_exata(self):
        from pharos.grafo import media_exata
        self.assertEqual(media_exata([1e16, 1.0, -1e16, 1.0]), 0.5)   # soma ingênua perde os 1.0

    def test_independe_da_ordem(self):
        import random
        from pharos.grafo import media_exata
        rnd = random.Random(7)
        valores = [rnd.uniform(0, 300) for _ in range(97)]
        esperado = media_exata(valores)
        for _ in range(20):
            rnd.shuffle(valores)
            self.assertEqual(media_exata(valores), esperado)


class TestSomaDosTrechos(unittest.TestCase):
    """O Python 3.12 passou a somar floats com compensação (Neumaier) no sum();
    o 3.8 soma da esquerda para a direita. O custo de uma alternativa precisa
    dar o mesmo último bit nas duas versões, senão o empate entre dois
    caminhos de mesmo custo muda de lado."""

    def test_custo_com_soma_exatamente_arredondada(self):
        from pharos.alternativas import Alternativa, Trecho
        trechos = [Trecho(linha="X", padrao="X_0", linhas_equivalentes=("X",), embarque=str(k),
                          desembarque=str(k + 1), paradas=[str(k), str(k + 1)], espera_s=0.1, bordo_s=0.1,
                          distancia_m=0.1, partidas_linha=1, partidas_combinadas=1) for k in range(10)]
        alt = Alternativa("0", "10", trechos, list(range(10)), np.zeros((2, 2)))
        self.assertEqual(alt.espera_s, 1.0)          # soma ingênua daria 0.9999999999999999
        self.assertEqual(alt.bordo_s, 1.0)
        self.assertEqual(alt.distancia_m, 1.0)
        self.assertEqual(alt.tempo_s, 2.0)


def load_tests(loader, tests, ignore):
    import doctest
    import pharos.grafo
    tests.addTests(doctest.DocTestSuite(pharos.grafo))
    return tests


if __name__ == "__main__":
    unittest.main()
