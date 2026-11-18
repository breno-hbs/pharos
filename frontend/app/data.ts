/** Paradas vêm da API (GET /paradas?selecionavel=true). */
export type Stop = { id: string; name: string; short: string; terminal: boolean };
export const findStop = (stops: readonly Stop[], id: string): Stop => stops.find((stop) => stop.id === id) ?? { id, name: "Parada", short: "Parada", terminal: false };

/** `criterio` é o valor do parâmetro `ordenar` da API. A API não calcula caminhada, então a preferência é a distância percorrida. */
export const preferences = [
  { id: "duration", name: "Menor duração", icon: "timer", criterio: "TEMPO" },
  { id: "distance", name: "Menor distância", icon: "route", criterio: "DISTANCIA" },
  { id: "transfers", name: "Menos baldeações", icon: "repeat", criterio: "BALDEACOES" },
] as const;

export type Preference = (typeof preferences)[number]["id"];
export type Trip = {
  origin: string;
  destination: string;
  time: string;
  preference: Preference;
};

/** O banco de exemplo tem trajetos calculados para o pico da manhã de dia útil (6h às 9h). */
export const defaultTime = "07:30";

export const categories = [
  { id: "theft", label: "Furto", icon: "hand" },
  { id: "dark", label: "Rua escura", icon: "moon" },
  { id: "other", label: "Outros", icon: "alert" },
] as const;

export type Category = (typeof categories)[number]["id"];
export type Participation = Partial<Record<Category, "confirmed" | "contested">>;

export const observations = {
  theft: {
    place: "Praça do Jardim Comercial",
    nearby: "Próximo ao Jardim Comercial",
    description: "Moradores relataram furto próximo ao ponto de ônibus.",
    date: "06 nov. 2026 · 17:50",
    count: 3,
  },
  dark: {
    place: "Estrada de Itapecerica",
    nearby: "Próximo à conexão Capão Redondo",
    description: "Trecho da calçada com pouca iluminação ao anoitecer, próximo ao ponto de ônibus.",
    date: "06 nov. 2026 · 18:35",
    count: 14,
  },
  other: {
    place: "Conexão Capão Redondo",
    nearby: "Próximo à conexão Capão Redondo",
    description: "Piso irregular junto à conexão de acesso. Atenção ao caminhar pelo trecho.",
    date: "07 nov. 2026 · 09:20",
    count: 18,
  },
} satisfies Record<Category, { place: string; nearby: string; description: string; date: string; count: number }>;

export const participationBand = (count: number) => count >= 15 ? "high" : count >= 5 ? "medium" : "low";

export type Route = {
  id: "a" | "b" | "c";
  idAlternativa: number;
  /** Estritamente menos baldeações que alguma outra alternativa. */
  fewestTransfers: boolean;
  caption: string;
  via: string;
  short: string;
  minutes: number;
  distanceKm: number;
  transfers: number;
  lines: string[];
  steps: { nrSequencia: number; cdLinha: string; nmParadaEmbarque: string; nmParadaDesembarque: string }[];
  indicators: { idIndicador: number; cdTipo: string; nmTipo: string; nrAno: number; tpFaixaHoraria: string; nrRaioM: number; qtOcorrencias: number; nmFonte: string; simulado: boolean }[];
  occurrences: number;
  /** Relatos comunitários simulados (a API não tem relatos). */
  warnings: readonly Category[];
};
export type RouteId = Route["id"];

export function offsetTime(time: string, offset: number) {
  const [hours, minutes] = time.split(":").map(Number);
  const total = (hours * 60 + minutes + offset) % (24 * 60);
  return [Math.floor(total / 60), total % 60].map((value) => String(value).padStart(2, "0")).join(":");
}

export function tripFromParams(params: Pick<URLSearchParams, "get">, stops: readonly Stop[]): Trip {
  const known = (id: string | null) => stops.find((stop) => stop.id === id)?.id;
  // Padrão: uma parada comum até o terminal, par que existe no banco de exemplo.
  const origin = known(params.get("origem")) ?? stops.find((stop) => !stop.terminal)?.id ?? stops[0]?.id ?? "";
  const destination = known(params.get("destino")) ?? stops.find((stop) => stop.terminal && stop.id !== origin)?.id ?? stops.find((stop) => stop.id !== origin)?.id ?? "";
  const time = params.get("hora");
  return {
    origin,
    destination: destination === origin ? stops.find((stop) => stop.id !== origin)?.id ?? "" : destination,
    time: time && /^([01]\d|2[0-3]):[0-5]\d$/.test(time) ? time : defaultTime,
    preference: preferences.find(({ id }) => id === params.get("preferencia"))?.id ?? "duration",
  };
}

export type PendingReport = {
  receipt: string;
  status: "PENDENTE";
  category: Category;
  location: Category;
  description: string;
};
