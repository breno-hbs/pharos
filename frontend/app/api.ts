import type { Category, Route, Stop, Trip } from "./data";
import { preferences } from "./data";

/** URL base da API Java (Render). Pode ser trocada com NEXT_PUBLIC_API_URL em .env.local. */
export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "https://pharos-api-kaxr.onrender.com").replace(/\/$/, "");

/** O plano gratuito do Render dorme; a primeira chamada pode levar cerca de 50 s. */
const TIMEOUT_MS = 90_000;

export class ApiError extends Error {
  constructor(message: string, readonly status = 0) {
    super(message);
  }
}

type Parada = { idParada: number; cdParadaGtfs: string; nmParada: string; nmMunicipio: string; flTerminal: string; flSelecionavel: string };
type Etapa = { nrSequencia: number; cdLinha: string; nmParadaEmbarque: string; nmParadaDesembarque: string };
type Indicador = { idIndicador: number; cdTipo: string; nmTipo: string; nrAno: number; tpFaixaHoraria: string; nrRaioM: number; qtOcorrencias: number; nmFonte: string; simulado: boolean };
type Alternativa = {
  alternativa: { idAlternativa: number; nrOrdem: number; nrTempoTotalMin: number; nrDistanciaKm: number; qtBaldeacoes: number };
  etapas: Etapa[];
  indicadores: Indicador[];
  totalOcorrencias: number;
};
export type TrajetoResposta = {
  idParOd: number | null;
  stResultado: string;
  mensagem: string | null;
  cenario: { cdCenario: string; nmCenario: string } | null;
  alternativas: Alternativa[];
};
export type Consulta = { idConsulta: number };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { Accept: "application/json", ...(init?.body ? { "Content-Type": "application/json" } : {}) },
    });
    if (!response.ok) {
      const body = await response.json().catch(() => null) as { mensagem?: string } | null;
      throw new ApiError(body?.mensagem ?? `A API respondeu com erro ${response.status}.`, response.status);
    }
    return await response.json() as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("Não foi possível falar com a API. Verifique a conexão e tente novamente.");
  } finally {
    clearTimeout(timer);
  }
}

const shorten = (name: string) => name.length > 30 ? `${name.slice(0, 29).trimEnd()}…` : name;

export async function fetchStops(): Promise<Stop[]> {
  const paradas = await request<Parada[]>("/paradas?selecionavel=true");
  return paradas.map((parada) => ({ id: String(parada.idParada), name: parada.nmParada, short: shorten(parada.nmParada), terminal: parada.flTerminal === "S" }));
}

export const criterioOf = (trip: Trip) => preferences.find(({ id }) => id === trip.preference)!.criterio;

/** O banco de exemplo calcula trajetos por cenário de dia útil; a hora (0 a 23) escolhe a janela. */
export function fetchTrajetos(trip: Trip) {
  const hora = Number(trip.time.slice(0, 2));
  const query = new URLSearchParams({ origem: trip.origin, destino: trip.destination, dia: "UTIL", hora: String(hora), ordenar: criterioOf(trip) });
  return request<TrajetoResposta>(`/trajetos?${query}`);
}

/** Registro anônimo da consulta (tabela PH_CONSULTA). Falhas aqui nunca atrapalham a tela. */
export function registerSearch(idParOd: number, criterio: string, elapsedMs: number) {
  return request<Consulta>("/consultas", {
    method: "POST",
    body: JSON.stringify({ idParOd, tpCriterioOrdenacao: criterio, nrTempoRespostaMs: elapsedMs, flTeste: "S" }),
  }).then(({ idConsulta }) => idConsulta).catch(() => undefined);
}

export function registerChoice(idConsulta: number, idAlternativaEscolhida: number) {
  return request<Consulta>(`/consultas/${idConsulta}`, { method: "PUT", body: JSON.stringify({ idAlternativaEscolhida }) }).catch(() => undefined);
}

const letters = ["a", "b", "c"] as const;
/** Relatos comunitários não existem na API: seguem simulados e ligados à posição da rota na ilustração. */
const demoWarnings: Record<(typeof letters)[number], readonly Category[]> = { a: ["theft", "dark", "other"], b: ["dark", "theft"], c: ["theft"] };

export function toRoutes(response: TrajetoResposta): Route[] {
  const list = response.alternativas;
  /** Só rotula "melhor em X" quando a rota é estritamente melhor que alguma outra, evitando empates sem sentido. */
  const wins = (item: Alternativa, pick: (value: Alternativa) => number) => list.some((other) => pick(other) > pick(item)) && list.every((other) => pick(other) >= pick(item));
  const time = (value: Alternativa) => value.alternativa.nrTempoTotalMin;
  const distance = (value: Alternativa) => value.alternativa.nrDistanciaKm;
  const transfers = (value: Alternativa) => value.alternativa.qtBaldeacoes;
  return list.map((item, index) => {
    const { alternativa } = item;
    const id = letters[Math.min(Math.max(alternativa.nrOrdem - 1, 0), 2)] ?? letters[index];
    const lines = item.etapas.map((etapa) => etapa.cdLinha).filter((line, position, all) => all.indexOf(line) === position);
    const caption = list.length === 1 ? "Única opção"
      : wins(item, time) ? "Menor duração"
      : wins(item, distance) ? "Menor distância"
      : wins(item, transfers) ? "Menos baldeações" : "Outra opção";
    return {
      id,
      fewestTransfers: wins(item, transfers),
      idAlternativa: alternativa.idAlternativa,
      caption,
      via: lines.length ? `linha ${lines.join(" + ")}` : "linha não informada",
      short: lines.length ? `linha ${lines.join(" + ")}` : "—",
      minutes: Math.round(alternativa.nrTempoTotalMin),
      distanceKm: alternativa.nrDistanciaKm,
      transfers: alternativa.qtBaldeacoes,
      lines,
      steps: [...item.etapas].sort((a, b) => a.nrSequencia - b.nrSequencia),
      indicators: item.indicadores,
      occurrences: item.totalOcorrencias,
      warnings: demoWarnings[id],
    };
  });
}
