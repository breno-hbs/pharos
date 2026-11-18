export const stops = [
  { id: "jardim", name: "Praça do Jardim Comercial", short: "Jd. Comercial" },
  { id: "metro", name: "Metrô Capão Redondo", short: "Metrô Capão Redondo" },
] as const;

export type StopId = (typeof stops)[number]["id"];
export const getStop = (id: StopId) => stops.find((stop) => stop.id === id)!;

export const preferences = [
  { id: "duration", name: "Menor duração", icon: "timer" },
  { id: "walking", name: "Menos caminhada", icon: "walk" },
  { id: "transfers", name: "Menos baldeações", icon: "repeat" },
] as const;

export type Preference = (typeof preferences)[number]["id"];
export type Trip = {
  origin: StopId;
  destination: StopId;
  time: string;
  preference: Preference;
};

export const defaultTrip: Trip = {
  origin: "jardim",
  destination: "metro",
  time: "18:10",
  preference: "duration",
};

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

export const routes = [
  { id: "a", caption: "Menor duração", via: "Estrada de Itapecerica", short: "Estr. de Itapecerica", minutes: 32, walking: 8, transfers: 0, lines: ["675K-10"], warnings: ["theft", "dark", "other"] },
  { id: "b", caption: "Menos caminhada", via: "Av. Ellis Maas", short: "Av. Ellis Maas", minutes: 39, walking: 5, transfers: 1, lines: ["6016-10", "675K-10"], warnings: ["dark", "theft"] },
  { id: "c", caption: "Outra opção", via: "Av. Comendador Sant’Anna", short: "Av. Com. Sant’Anna", minutes: 44, walking: 12, transfers: 0, lines: ["6820-10"], warnings: ["theft"] },
] as const;

export type Route = (typeof routes)[number];
export type RouteId = Route["id"];

export function orderedRoutes(preference: Preference) {
  const metric = preference === "duration" ? "minutes" : preference;
  return [...routes].sort((a, b) => a[metric] - b[metric] || a.minutes - b.minutes);
}

export function offsetTime(time: string, offset: number) {
  const [hours, minutes] = time.split(":").map(Number);
  const total = (hours * 60 + minutes + offset) % (24 * 60);
  return [Math.floor(total / 60), total % 60].map((value) => String(value).padStart(2, "0")).join(":");
}

export function tripFromParams(params: Pick<URLSearchParams, "get">): Trip {
  const origin = params.get("origem") === "metro" ? "metro" : "jardim";
  const preference = params.get("preferencia");
  const time = params.get("hora");
  return {
    origin,
    destination: origin === "metro" ? "jardim" : "metro",
    time: time && /^([01]\d|2[0-3]):[0-5]\d$/.test(time) ? time : defaultTrip.time,
    preference: preferences.find(({ id }) => id === preference)?.id ?? defaultTrip.preference,
  };
}


export function hasMockConnection(trip: Trip) {
  return trip.origin === "jardim" && trip.destination === "metro";
}

export type PendingReport = {
  receipt: string;
  status: "PENDENTE";
  category: Category;
  location: Category;
  description: string;
};
