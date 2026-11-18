"""Testes de tratamento de erros e da interface (menu e linha de comando)."""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

import main
from pharos.grafo import carregar_rede, hhmm_para_s, s_para_hhmm


def roteiro(*respostas):
    """Função `entrada` que devolve as respostas em ordem (simula o teclado)."""
    fila = iter(respostas)

    def entrada(_prompt=""):
        try:
            return next(fila)
        except StopIteration:
            raise EOFError from None
    return entrada


class TestErros(unittest.TestCase):
    def test_horarios(self):
        self.assertEqual(hhmm_para_s("07:30"), 27000)
        self.assertEqual(hhmm_para_s("25:10"), 90600)      # GTFS permite > 24h
        self.assertEqual(s_para_hhmm(90600), "01:10 (+1 dia)")
        for ruim in ("7h30", "07:60", "abc", "", "48:00"):
            with self.assertRaises(ValueError, msg=ruim):
                hhmm_para_s(ruim)

    def test_rede_inexistente_ou_invalida(self):
        with self.assertRaises(FileNotFoundError):
            carregar_rede("nao_existe.json")
        with tempfile.TemporaryDirectory() as d:
            ruim = os.path.join(d, "ruim.json")
            with open(ruim, "w") as f:
                f.write("{ isto não é json")
            with self.assertRaises(ValueError):
                carregar_rede(ruim)
            incompleto = os.path.join(d, "incompleto.json")
            with open(incompleto, "w") as f:
                json.dump({"meta": {}}, f)
            with self.assertRaises(ValueError):
                carregar_rede(incompleto)

    def test_extracao_rejeita_arquivo_que_nao_e_gtfs(self):
        from pharos.extracao_gtfs import extrair
        with tempfile.TemporaryDirectory() as d:
            falso = os.path.join(d, "falso.zip")
            with open(falso, "w") as f:
                f.write("não é zip")
            with self.assertRaises(ValueError):
                extrair(falso, os.path.join(d, "saida.json"), verbose=False)


@unittest.skipUnless(os.path.exists(main.REDE), "rede piloto não gerada")
class TestInterface(unittest.TestCase):
    def test_menu_consulta_e_saida(self):
        saida = []
        # 1 = comparar; origem 1 (13211); destino 3 (407); cenário padrão;
        # critério padrão; simular às 07:00; 0 = sair
        main.menu(roteiro("1", "1", "3", "", "", "07:00", "0"), saida.append)
        texto = "\n".join(saida)
        self.assertIn("ALTERNATIVAS_DISTINTAS", texto)
        self.assertIn("linha 551", texto)
        self.assertIn("linha 193", texto)
        self.assertIn("551 07:04->07:28", texto)
        self.assertIn("Até logo.", texto)

    def test_menu_entradas_invalidas_nao_quebram(self):
        saida = []
        main.menu(roteiro("9", "1", "abc", "3", "", "", "", "1", "1", "3", "7", "0"), saida.append)
        texto = "\n".join(saida)
        self.assertIn("Opção inválida.", texto)
        self.assertIn("parada abc fora da rede piloto", texto)
        self.assertIn("opção inválida: '7'", texto)
        self.assertIn("Até logo.", texto)

    def test_menu_fim_da_entrada(self):
        saida = []
        main.menu(roteiro(), saida.append)          # EOF logo no início
        self.assertIn("Até logo.", "\n".join(saida))

    def test_linha_de_comando(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            self.assertEqual(main.main(["consultar", "13211", "407"]), 0)
            self.assertEqual(main.main(["consultar", "99999", "407"]), 1)
            self.assertEqual(main.main(["consultar", "13211", "407", "--hora", "7h"]), 1)
        self.assertIn("ALTERNATIVAS_DISTINTAS", out.getvalue())
        self.assertIn("fora da rede piloto", err.getvalue())
        self.assertIn("horário inválido", err.getvalue())

    def test_cenario_aceita_codigo_do_banco_em_minusculas(self):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            self.assertEqual(main.main(["consultar", "13211", "407", "--cenario", "util_tarde"]), 0)
        self.assertIn("Dia útil, 17h00-20h00", out.getvalue())

    def test_exportar_recusa_entrada_invalida_antes_de_gravar(self):
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            self.assertEqual(main.main(["exportar", "--cenarios", "util_pico_manha"]), 1)
            self.assertEqual(main.main(["exportar", "--data-calculo", "17/11/2026"]), 1)
        self.assertIn("cenário desconhecido", err.getvalue())
        self.assertIn("AAAA-MM-DD", err.getvalue())


if __name__ == "__main__":
    unittest.main()
