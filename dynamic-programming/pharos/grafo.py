"""Modelo de grafo do piloto.

Vértice   parada física do GTFS (stop_id) dentro do recorte.
Aresta    viagem em UMA linha (padrão de viagem = linha + sentido + traçado),
          sem baldeação: embarque na parada u e desembarque numa parada v
          posterior a u no mesmo padrão. O grafo é dirigido e respeita o sentido.
          Entre o mesmo par (u, v) pode haver arestas paralelas (linhas
          diferentes); a matriz de custos guarda a menor e qual linha a gerou.
Baldeação troca de aresta num vértice: desce de uma linha e embarca em outra na
          mesma parada. Baldeações a pé entre paradas diferentes NÃO são
          modeladas (o GTFS não traz rede de pedestres nem transfers.txt).

Saltos    trecho entre duas paradas consecutivas de um padrão. A ARTESP distribui
          o tempo de cada viagem de forma uniforme entre as paradas, então duas
          linhas no mesmo trecho de rua recebem tempos diferentes só porque suas
          rotas completas têm durações diferentes. Para não criar diferenças
          artificiais, cada salto recebe UM valor canônico de tempo e distância:
          a média entre as linhas que o percorrem, ponderada pelo nº de viagens
          do dia (viagens duplicadas contam uma vez). Tempo e distância de uma
          aresta são a soma dos saltos, logo são aditivos.

Pesos por critério (cenário = tipo de dia + janela horária):
  tempo      espera estimada da linha + tempo a bordo
             espera = (janela / nº de partidas da linha em u na janela) / 2
             (hipótese: chegada aleatória do passageiro e intervalo regular)
  distancia  soma das distâncias canônicas dos saltos + 1 mm por embarque
  embarques  1 por aresta + 1e-6 por metro (desempate pela distância)
Arestas sem partida na janela não existem naquele cenário.

Propriedade garantida por esse modelo: dividir uma viagem em duas na mesma
sequência de paradas nunca reduz o custo (só acrescenta espera, 1 mm ou 1
embarque). Por isso os caminhos mínimos do Floyd-Warshall nunca contêm
baldeações inúteis; o teste `test_otimos_sao_validos` verifica isso em todos os
pares da rede.

Linhas no mesmo itinerário (mesma sequência de paradas entre u e v) aparecem
como uma única alternativa na saída, com a lista de linhas equivalentes. Somar
as frequências delas no cálculo do caminho exigiria um modelo de estratégias
ótimas (hipercaminhos), fora do escopo do piloto; o critério tempo usa a espera
da linha escolhida, o que é conservador onde várias linhas atendem o trecho.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass

import numpy as np

from . import config
from .geo import para_xy


def media_exata(valores) -> float:
    """Média com soma exatamente arredondada (math.fsum).

    Não depende da ordem dos valores nem da versão do NumPy. Assim, dois
    caminhos de mesmo custo empatam do mesmo jeito em qualquer computador.

    >>> media_exata([1e16, 1.0, -1e16, 1.0])
    0.5
    """
    valores = list(valores)
    return math.fsum(valores) / len(valores)


def hhmm_para_s(hhmm: str) -> int:
    """'HH:MM' -> segundos desde 00:00. Aceita HH até 47 (o GTFS passa de 24h)."""
    try:
        h, m = str(hhmm).strip().split(":")
        h, m = int(h), int(m)
    except ValueError:
        raise ValueError(f"horário inválido: {hhmm!r} (use HH:MM, ex.: 07:30)") from None
    if not (0 <= h <= 47 and 0 <= m <= 59):
        raise ValueError(f"horário fora do intervalo: {hhmm!r}")
    return h * 3600 + m * 60


def s_para_hhmm(s: float) -> str:
    """Segundos desde 00:00 do dia de serviço -> HH:MM (o GTFS permite > 24h)."""
    s = int(round(s))
    h, m = s // 3600, (s % 3600) // 60
    return f"{h:02d}:{m:02d}" if h < 24 else f"{h - 24:02d}:{m:02d} (+1 dia)"


@dataclass
class Aresta:
    u: str
    v: str
    intermediarias: tuple
    padrao: str
    linha: str
    n_partidas: int
    espera_s: float
    bordo_s: float
    distancia_m: float

    @property
    def itinerario(self):
        return (self.u, self.v, self.intermediarias)

    def peso(self, criterio: str) -> float:
        if criterio == "tempo":
            return self.espera_s + self.bordo_s
        if criterio == "distancia":
            return self.distancia_m + config.EPS_EMBARQUE_M
        if criterio == "embarques":
            return 1.0 + config.EPS_DISTANCIA_EMB * self.distancia_m
        raise ValueError(f"critério desconhecido: {criterio}")


class Grafo:
    """Grafo dirigido de paradas para um cenário temporal."""

    def __init__(self, rede: dict, cenario: str = config.CENARIO_PADRAO):
        if cenario not in config.CENARIOS:
            raise ValueError(f"cenário desconhecido: {cenario}")
        self.rede = rede
        self.cenario = cenario
        c = config.CENARIOS[cenario]
        self.service_id = c["service_id"]
        self.w0, self.w1 = hhmm_para_s(c["inicio"]), hhmm_para_s(c["fim"])
        self.janela_s = self.w1 - self.w0
        self.padroes = {p["id"]: p for p in rede["padroes"]}
        self.paradas = rede["paradas"]
        self._saltos_canonicos()
        self._arestas()
        self.vertices = sorted({s for s, info in self.paradas.items() if info["no_recorte"]}, key=_ordem_id)
        self.idx = {s: i for i, s in enumerate(self.vertices)}
        self.saindo, self.chegando, self.por_itinerario = {}, {}, {}
        for ai, a in enumerate(self.arestas):
            self.saindo.setdefault(a.u, []).append(ai)
            self.chegando.setdefault(a.v, []).append(ai)
            self.por_itinerario.setdefault(a.itinerario, []).append(ai)

    # ------------------------------------------------------------ construção
    def _saltos_canonicos(self):
        acum = {}
        for p in self.rede["padroes"]:
            seq, off, pos = p["paradas"], p["offset_s"], p["pos_m"]
            for t0 in p["partidas"].get(self.service_id, []):
                chave_viagem = (p["route_id"], p["direction_id"], t0)
                for k in range(len(seq) - 1):
                    acum.setdefault((seq[k], seq[k + 1]), {}).setdefault(
                        chave_viagem, (off[k + 1] - off[k], pos[k + 1] - pos[k]))
        self.saltos, self.faixa_saltos = {}, {}
        for h, d in acum.items():
            v = np.array(list(d.values()))
            self.saltos[h] = (media_exata(v[:, 0].tolist()), media_exata(v[:, 1].tolist()))
            self.faixa_saltos[h] = {"tempo_s": (float(v[:, 0].min()), float(v[:, 0].max())),
                                    "distancia_m": (float(v[:, 1].min()), float(v[:, 1].max())),
                                    "viagens": len(d)}

    def _arestas(self):
        self.arestas = []
        for p in self.rede["padroes"]:
            seq, dentro, off = p["paradas"], p["no_recorte"], p["offset_s"]
            inicios = sorted(set(p["partidas"].get(self.service_id, [])))
            if not inicios:
                continue
            # soma acumulada dos saltos canônicos ao longo do padrão
            ct, cd = [0.0], [0.0]
            for k in range(len(seq) - 1):
                t, d = self.saltos[(seq[k], seq[k + 1])]
                ct.append(ct[-1] + t)
                cd.append(cd[-1] + d)
            idx = [i for i, x in enumerate(dentro) if x]
            for a, i in enumerate(idx):
                n = sum(1 for t0 in inicios if self.w0 <= t0 + off[i] < self.w1)
                if n == 0:
                    continue
                espera = self.janela_s / n / 2.0
                for j in idx[a + 1:]:
                    self.arestas.append(Aresta(seq[i], seq[j], tuple(seq[i + 1:j]), p["id"], p["route_id"],
                                               n, espera, ct[j] - ct[i], cd[j] - cd[i]))

    # ---------------------------------------------------------------- pesos
    def matriz(self, criterio: str):
        """Matriz de custos n×n (lista de listas) e, por par, a aresta mínima."""
        n = len(self.vertices)
        INF = float("inf")
        W = [[INF] * n for _ in range(n)]
        arg = {}
        for i in range(n):
            W[i][i] = 0.0
        for ai, a in enumerate(self.arestas):
            i, j = self.idx[a.u], self.idx[a.v]
            w = a.peso(criterio)
            if w < W[i][j]:          # empate: mantém a primeira aresta (ordem determinística)
                W[i][j] = w
                arg[(i, j)] = ai
        return W, arg

    # ------------------------------------------------------------ utilidades
    def nome(self, stop_id: str) -> str:
        return self.paradas[stop_id]["nome"]

    def equivalentes(self, a: Aresta):
        """Arestas de outras linhas com exatamente o mesmo itinerário u→v."""
        return [self.arestas[k] for k in self.por_itinerario[a.itinerario]]

    def partidas_combinadas(self, a: Aresta) -> int:
        """Partidas na janela em u somando todas as linhas do mesmo itinerário
        (viagens duplicadas da mesma linha/sentido/horário contam uma vez)."""
        vistos = set()
        for e in self.equivalentes(a):
            p = self.padroes[e.padrao]
            i = p["paradas"].index(a.u)
            for t0 in p["partidas"].get(self.service_id, []):
                t = t0 + p["offset_s"][i]
                if self.w0 <= t < self.w1:
                    vistos.add((p["route_id"], p["direction_id"], round(t)))
        return len(vistos)

    def xy_aresta(self, a: Aresta) -> np.ndarray:
        """Geometria do trecho u→v no traçado da própria linha."""
        p = self.padroes[a.padrao]
        coords = np.asarray(p["geometria"]["coords"], dtype=float)
        xy = para_xy(coords[:, 0], coords[:, 1])
        cum = p["geometria"]["inicio_m"] + np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(xy, axis=0).T))])
        p0, p1 = p["pos_m"][p["paradas"].index(a.u)], p["pos_m"][p["paradas"].index(a.v)]
        x0, y0 = np.interp(p0, cum, xy[:, 0]), np.interp(p0, cum, xy[:, 1])
        x1, y1 = np.interp(p1, cum, xy[:, 0]), np.interp(p1, cum, xy[:, 1])
        meio = xy[(cum > p0) & (cum < p1)]
        return np.vstack([[x0, y0], meio, [x1, y1]])

    def tamanho(self) -> dict:
        return {"vertices": len(self.vertices), "arestas": len(self.arestas),
                "pares_com_aresta": len({(a.u, a.v) for a in self.arestas}),
                "itinerarios_distintos": len(self.por_itinerario)}


def _ordem_id(s: str):
    return (0, int(s)) if s.isdigit() else (1, s)


def carregar_rede(caminho: str) -> dict:
    """Lê dados/rede_piloto.json e confere a estrutura mínima."""
    try:
        with open(caminho, encoding="utf-8") as f:
            rede = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"rede piloto não encontrada em {caminho}. "
                                "Gere com: python main.py extrair --gtfs <artesp_gtfs.zip>") from None
    except json.JSONDecodeError as e:
        raise ValueError(f"{caminho} não é um JSON válido (linha {e.lineno}): regenere a rede") from None
    faltando = [k for k in ("meta", "linhas", "paradas", "padroes") if k not in rede]
    if faltando:
        raise ValueError(f"{caminho} incompleto, faltam as chaves {faltando}")
    return rede
