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
