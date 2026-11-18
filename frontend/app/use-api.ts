"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError, criterioOf, fetchStops, fetchTrajetos, registerChoice, registerSearch, toRoutes, type TrajetoResposta } from "./api";
import type { Route, Stop, Trip } from "./data";

export type Remote<T> =
  | { status: "loading"; slow: boolean }
  | { status: "error"; message: string }
  | { status: "ok"; data: T };

function useSlow(loading: boolean) {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    if (!loading) return;
    const timer = setTimeout(() => setSlow(true), 4000);
    return () => { clearTimeout(timer); setSlow(false); };
  }, [loading]);
  return slow;
}

const messageOf = (error: unknown) => error instanceof ApiError ? error.message : "Erro inesperado ao consultar a API.";

export function useStops(attempt: number): Remote<Stop[]> {
  const [state, setState] = useState<{ attempt: number; result: Remote<Stop[]> } | null>(null);
  useEffect(() => {
    let active = true;
    fetchStops().then(
      (data) => active && setState({ attempt, result: { status: "ok", data } }),
      (error) => active && setState({ attempt, result: { status: "error", message: messageOf(error) } }),
    );
    return () => { active = false; };
  }, [attempt]);
  const loading = state?.attempt !== attempt;
  const slow = useSlow(loading);
  return loading ? { status: "loading", slow } : state.result;
}

export type Trajetos = { routes: Route[]; response: TrajetoResposta };

/** Busca os trajetos quando a tela precisa deles. `trip` nulo = nada a buscar. */
export function useTrajetos(trip: Trip | null, attempt: number): { remote: Remote<Trajetos>; choose: (idAlternativa: number) => void } {
  const key = trip ? `${trip.origin}|${trip.destination}|${trip.time.slice(0, 2)}|${criterioOf(trip)}|${attempt}` : "";
  const [state, setState] = useState<{ key: string; result: Remote<Trajetos> } | null>(null);
  const logged = useRef(new Map<string, Promise<number | undefined>>());

  useEffect(() => {
    if (!trip) return;
    let active = true;
    const started = performance.now();
    fetchTrajetos(trip).then(
      (response) => {
        if (!active) return;
        const routes = toRoutes(response);
        setState({ key, result: { status: "ok", data: { routes, response } } });
        // Uma consulta por pesquisa: não registra de novo ao reordenar sem mudar de pesquisa.
        if (response.idParOd != null && routes.length && !logged.current.has(key)) {
          logged.current.set(key, registerSearch(response.idParOd, criterioOf(trip), Math.round(performance.now() - started)));
        }
      },
      (error) => active && setState({ key, result: { status: "error", message: messageOf(error) } }),
    );
    return () => { active = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  /** Atualiza a consulta registrada com a alternativa que a pessoa abriu nos detalhes. */
  const choose = (idAlternativa: number) => {
    logged.current.get(key)?.then((idConsulta) => { if (idConsulta) void registerChoice(idConsulta, idAlternativa); });
  };

  const loading = Boolean(trip) && state?.key !== key;
  const slow = useSlow(loading);
  if (!trip || loading || !state) return { remote: { status: "loading", slow: trip ? slow : false }, choose };
  return { remote: state.result, choose };
}
