"""Testes do exportador: os arquivos seguem o modelo oficial do banco Pharos.

Referência: database/02_ddl.sql e database/03_dml.sql do repositório da equipe
(github.com/breno-hbs/pharos). Os nomes de colunas e os CHECKs abaixo foram
copiados desse DDL de propósito, sem importar nada do exportador, para que uma
divergência entre o código Python e o banco apareça como falha de teste.

As chaves substitutas (id_*) são IDENTITY no Oracle e não vão nos CSVs. Cada
chave estrangeira é exportada pela chave natural (coluna UNIQUE) da tabela
referenciada: cd_cenario, cd_parada_gtfs, cd_linha e nm_fonte.
"""
import csv
import os
import re
import tempfile
import unittest

from pharos import config
from pharos.exportar import exportar
from pharos.grafo import carregar_rede

REDE = os.path.join(os.path.dirname(__file__), "..", "dados", "rede_piloto.json")

# Os 7 pontos que o DML do banco já usa (ph_parada, ids 1 a 7).
PONTOS = ["407", "13211", "13466", "32960", "21657", "405", "2201"]
DATA = "2026-11-17"

COLUNAS = {
    "ph_cenario": ["cd_cenario", "nm_cenario", "tp_dia", "nr_hora_inicio", "nr_hora_fim"],
    "ph_parada": ["cd_parada_gtfs", "nm_parada", "nm_municipio", "nr_latitude", "nr_longitude",
                  "fl_terminal", "fl_selecionavel", "nm_fonte"],
    "ph_linha": ["cd_linha", "ds_itinerario", "tp_modal", "nm_fonte"],
    "ph_par_origem_destino": ["cd_cenario", "cd_parada_origem", "cd_parada_destino", "st_resultado",
                              "dt_calculo", "nm_fonte"],
    "ph_alternativa": ["cd_cenario", "cd_parada_origem", "cd_parada_destino", "nr_ordem",
                       "nr_tempo_total_min", "nr_distancia_km", "qt_baldeacoes"],
    "ph_etapa_trajeto": ["cd_cenario", "cd_parada_origem", "cd_parada_destino", "nr_ordem", "nr_sequencia",
                         "cd_linha", "cd_parada_embarque", "cd_parada_desembarque"],
}

# ph_cenario no DML do banco (database/03_dml.sql).
CENARIOS_BANCO = {
    "UTIL_MANHA": ("Dia útil - pico da manhã", "UTIL", 6, 9),
    "UTIL_TARDE": ("Dia útil - pico da tarde", "UTIL", 17, 20),
    "UTIL_NOITE": ("Dia útil - noite", "UTIL", 20, 24),
    "SABADO_MANHA": ("Sábado - manhã", "SABADO", 8, 12),
    "DOMINGO_MANHA": ("Domingo - manhã", "DOMINGO", 8, 11),
}
FONTE_GTFS = "GTFS ARTESP - transporte intermunicipal"
FONTE_CALCULO = "Cálculo Pharos - Floyd-Warshall (módulo Dynamic Programming)"
MUNICIPIO_NO_DML = {"407": "São Paulo", "13211": "Embu das Artes", "13466": "Embu das Artes",
                    "32960": "São Paulo", "21657": "São Paulo", "405": "São Paulo", "2201": "São Paulo"}


def ler(pasta, tabela):
    with open(os.path.join(pasta, tabela + ".csv"), encoding="utf-8", newline="") as f:
        leitor = csv.reader(f)
        cabecalho = next(leitor)
        return cabecalho, [dict(zip(cabecalho, linha)) for linha in leitor]


def cabe(texto, tamanho):
    """VARCHAR2(n) no Oracle conta bytes por padrão (NLS_LENGTH_SEMANTICS=BYTE)."""
    return len(texto.encode("utf-8")) <= tamanho


def decimal_ok(texto, inteiros, casas):
    return re.fullmatch(rf"\d{{1,{inteiros}}}\.\d{{{casas}}}", texto) is not None


@unittest.skipUnless(os.path.exists(REDE), "rede piloto não gerada")
class TestExportacaoModeloOficial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.rede = carregar_rede(REDE)
        cls.res = exportar(cls.rede, cls.tmp.name, cenarios=["UTIL_MANHA"], pontos=PONTOS,
                           data_calculo=DATA, verbose=False)
        cls.cab, cls.t = {}, {}
        for tabela in COLUNAS:
            cls.cab[tabela], cls.t[tabela] = ler(cls.tmp.name, tabela)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    # ------------------------------------------------------ estrutura
    def test_cabecalhos_seguem_o_ddl_oficial(self):
        for tabela, colunas in COLUNAS.items():
            self.assertEqual(self.cab[tabela], colunas, tabela)

    def test_nao_gera_mais_os_csvs_do_modelo_antigo(self):
        for antigo in ("parada.csv", "linha.csv", "par_consulta.csv", "alternativa.csv",
                       "alternativa_trecho.csv", "alternativa_parada.csv"):
            self.assertFalse(os.path.exists(os.path.join(self.tmp.name, antigo)), antigo)

    def test_cenarios_iguais_ao_dml_do_banco(self):
        obtido = {r["cd_cenario"]: (r["nm_cenario"], r["tp_dia"], int(r["nr_hora_inicio"]), int(r["nr_hora_fim"]))
                  for r in self.t["ph_cenario"]}
        self.assertEqual(obtido, CENARIOS_BANCO)

    def test_config_usa_os_codigos_de_cenario_do_banco(self):
        self.assertEqual(set(config.CENARIOS), set(CENARIOS_BANCO))
        self.assertIn(config.CENARIO_PADRAO, CENARIOS_BANCO)

    def test_cenario_desconhecido_e_recusado(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            exportar(self.rede, tmp, cenarios=["util_pico_manha"], pontos=PONTOS, verbose=False)

    # ---------------------------------------------- CHECKs e tamanhos
    def test_paradas_respeitam_o_ddl(self):
        codigos = [r["cd_parada_gtfs"] for r in self.t["ph_parada"]]
        self.assertEqual(len(codigos), len(set(codigos)))
        for r in self.t["ph_parada"]:
            self.assertTrue(cabe(r["cd_parada_gtfs"], 20) and cabe(r["nm_parada"], 150), r)
            self.assertTrue(r["nm_municipio"] and cabe(r["nm_municipio"], 60), r)
            self.assertTrue(-90 <= float(r["nr_latitude"]) <= 90 and -180 <= float(r["nr_longitude"]) <= 180)
            self.assertRegex(r["nr_latitude"], r"^-?\d{1,3}\.\d{1,6}$")
            self.assertIn(r["fl_terminal"], ("S", "N"))
            self.assertIn(r["fl_selecionavel"], ("S", "N"))
            self.assertEqual(r["nm_fonte"], FONTE_GTFS)

    def test_linhas_respeitam_o_ddl(self):
        codigos = [r["cd_linha"] for r in self.t["ph_linha"]]
        self.assertEqual(len(codigos), len(set(codigos)))
        self.assertEqual(set(codigos), set(self.rede["linhas"]))
        for r in self.t["ph_linha"]:
            self.assertTrue(cabe(r["cd_linha"], 20) and r["ds_itinerario"] and cabe(r["ds_itinerario"], 300))
            self.assertEqual(r["tp_modal"], "ONIBUS")
            self.assertEqual(r["nm_fonte"], FONTE_GTFS)

    def test_pares_respeitam_o_ddl(self):
        chaves = [(r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"]) for r in self.t["ph_par_origem_destino"]]
        self.assertEqual(len(chaves), len(set(chaves)))
        self.assertEqual(len(chaves), len(PONTOS) * (len(PONTOS) - 1))
        for r in self.t["ph_par_origem_destino"]:
            self.assertNotEqual(r["cd_parada_origem"], r["cd_parada_destino"])
            self.assertIn(r["st_resultado"], ("COM_ALTERNATIVAS", "SEM_TRAJETO", "SEM_TRAJETO_RAZOAVEL"))
            self.assertEqual(r["dt_calculo"], DATA)
            self.assertEqual(r["nm_fonte"], FONTE_CALCULO)

    def test_alternativas_respeitam_o_ddl(self):
        chaves = [(r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"], r["nr_ordem"])
                  for r in self.t["ph_alternativa"]]
        self.assertEqual(len(chaves), len(set(chaves)))
        self.assertTrue(self.t["ph_alternativa"])
        for r in self.t["ph_alternativa"]:
            self.assertGreaterEqual(int(r["nr_ordem"]), 1)
            self.assertTrue(decimal_ok(r["nr_tempo_total_min"], 4, 1), r)     # NUMBER(5,1)
            self.assertTrue(decimal_ok(r["nr_distancia_km"], 4, 2), r)        # NUMBER(6,2)
            self.assertGreater(float(r["nr_tempo_total_min"]), 0)
            self.assertGreater(float(r["nr_distancia_km"]), 0)
            self.assertIn(int(r["qt_baldeacoes"]), (0, 1, 2))

    def test_ordem_das_alternativas_e_continua(self):
        por_par = {}
        for r in self.t["ph_alternativa"]:
            por_par.setdefault((r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"]), []).append(int(r["nr_ordem"]))
        for par, ordens in por_par.items():
            self.assertEqual(sorted(ordens), list(range(1, len(ordens) + 1)), par)

    def test_etapas_respeitam_o_ddl(self):
        chaves = [(r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"], r["nr_ordem"], r["nr_sequencia"])
                  for r in self.t["ph_etapa_trajeto"]]
        self.assertEqual(len(chaves), len(set(chaves)))
        for r in self.t["ph_etapa_trajeto"]:
            self.assertTrue(1 <= int(r["nr_sequencia"]) <= 99)                # NUMBER(2), >= 1
            self.assertNotEqual(r["cd_parada_embarque"], r["cd_parada_desembarque"])

    # --------------------------------------- integridade referencial
    def test_chaves_estrangeiras_resolvem(self):
        cenarios = {r["cd_cenario"] for r in self.t["ph_cenario"]}
        paradas = {r["cd_parada_gtfs"] for r in self.t["ph_parada"]}
        linhas = {r["cd_linha"] for r in self.t["ph_linha"]}
        pares = {(r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"]): r["st_resultado"]
                 for r in self.t["ph_par_origem_destino"]}
        alts = {(r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"], r["nr_ordem"])
                for r in self.t["ph_alternativa"]}
        for (cen, o, d), _ in pares.items():
            self.assertIn(cen, cenarios)
            self.assertTrue({o, d} <= paradas)
        for cen, o, d, _ in alts:
            self.assertEqual(pares[(cen, o, d)], "COM_ALTERNATIVAS")
        for r in self.t["ph_etapa_trajeto"]:
            self.assertIn((r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"], r["nr_ordem"]), alts)
            self.assertIn(r["cd_linha"], linhas)
            self.assertTrue({r["cd_parada_embarque"], r["cd_parada_desembarque"]} <= paradas)

    def test_status_bate_com_a_quantidade_de_alternativas(self):
        n = {}
        for r in self.t["ph_alternativa"]:
            k = (r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"])
            n[k] = n.get(k, 0) + 1
        for r in self.t["ph_par_origem_destino"]:
            k = (r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"])
            self.assertEqual(r["st_resultado"] == "COM_ALTERNATIVAS", n.get(k, 0) > 0, k)

    def test_etapas_encadeiam_origem_baldeacoes_e_destino(self):
        etapas = {}
        for r in self.t["ph_etapa_trajeto"]:
            k = (r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"], r["nr_ordem"])
            etapas.setdefault(k, []).append(r)
        for r in self.t["ph_alternativa"]:
            k = (r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"], r["nr_ordem"])
            seq = sorted(etapas[k], key=lambda e: int(e["nr_sequencia"]))
            self.assertEqual([int(e["nr_sequencia"]) for e in seq], list(range(1, len(seq) + 1)))
            self.assertEqual(len(seq), int(r["qt_baldeacoes"]) + 1, k)
            self.assertEqual(seq[0]["cd_parada_embarque"], k[1])
            self.assertEqual(seq[-1]["cd_parada_desembarque"], k[2])
            for a, b in zip(seq, seq[1:]):
                self.assertEqual(a["cd_parada_desembarque"], b["cd_parada_embarque"])  # baldeação na mesma parada

    # ------------------------------------------------ valores do caso
    def test_par_13211_407_tem_as_duas_alternativas_validadas(self):
        alts = sorted((r for r in self.t["ph_alternativa"]
                       if (r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"]) == ("UTIL_MANHA", "13211", "407")),
                      key=lambda r: int(r["nr_ordem"]))
        self.assertEqual([(a["nr_tempo_total_min"], a["nr_distancia_km"], a["qt_baldeacoes"]) for a in alts],
                         [("29.4", "6.00", "0"), ("44.1", "8.97", "0")])
        linhas = [e["cd_linha"] for e in sorted(
            (e for e in self.t["ph_etapa_trajeto"]
             if (e["cd_cenario"], e["cd_parada_origem"], e["cd_parada_destino"]) == ("UTIL_MANHA", "13211", "407")),
            key=lambda e: int(e["nr_ordem"]))]
        self.assertEqual(linhas, ["551", "193"])

    def test_municipio_nao_e_inventado(self):
        paradas = {r["cd_parada_gtfs"]: r for r in self.t["ph_parada"]}
        for cd, municipio in MUNICIPIO_NO_DML.items():
            self.assertEqual(paradas[cd]["nm_municipio"], municipio, cd)
        validos = {"São Paulo", "Embu das Artes", "Itapecerica da Serra", "Taboão da Serra", "NÃO INFORMADO"}
        for r in self.t["ph_parada"]:
            self.assertIn(r["nm_municipio"], validos, r["cd_parada_gtfs"])

    def test_flags_de_parada(self):
        paradas = {r["cd_parada_gtfs"]: r for r in self.t["ph_parada"]}
        self.assertEqual(paradas["407"]["fl_terminal"], "S")
        self.assertEqual(paradas["13211"]["fl_terminal"], "N")
        for cd, r in paradas.items():
            self.assertEqual(r["fl_selecionavel"] == "S", cd in PONTOS, cd)

    def test_arquivos_complementares_usam_a_chave_natural(self):
        comp = os.path.join(self.tmp.name, "complementar")
        for nome in ("alternativa_detalhe.csv", "etapa_detalhe.csv", "sequencia_paradas.csv", "alternativas.geojson"):
            self.assertTrue(os.path.exists(os.path.join(comp, nome)), nome)
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "metadados.json")))
        cab, linhas = ler(comp, "sequencia_paradas")
        self.assertEqual(cab[:4], ["cd_cenario", "cd_parada_origem", "cd_parada_destino", "nr_ordem"])
        alts = {(r["cd_cenario"], r["cd_parada_origem"], r["cd_parada_destino"], r["nr_ordem"])
                for r in self.t["ph_alternativa"]}
        self.assertEqual({tuple(r[c] for c in cab[:4]) for r in linhas}, alts)


if __name__ == "__main__":
    unittest.main()
