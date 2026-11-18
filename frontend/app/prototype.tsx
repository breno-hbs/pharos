"use client";

import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { categories, tripFromParams, type Category, type Participation, type PendingReport, type RouteId, type Trip } from "./data";
import { MapView } from "./map";
import { Observation, ReportForm } from "./observations";
import { Planning } from "./planning";
import { Comparison, Details, HistoryCard } from "./routes";
import { Icon, Legend } from "./ui";
import { useStops, useTrajetos, type Remote } from "./use-api";
import { useViewMotion } from "./view-motion";

const screens = {
  home: "",
  plan: "planejamento",
  compare: "comparacao",
  detail: "detalhes",
  report: "observacao",
} as const;
type Screen = keyof typeof screens;
const screenOrder = Object.keys(screens) as Screen[];

function StatusPanel({ remote, onRetry, subject }: { remote: Remote<unknown>; onRetry: () => void; subject: string }) {
  if (remote.status === "error") {
    return (
      <div className="panel-content empty-results" role="alert">
        <h1>Não deu para carregar {subject}</h1>
        <p className="section-description">{remote.message}</p>
        <button type="button" className="button primary" onClick={onRetry}>Tentar de novo</button>
      </div>
    );
  }
  return (
    <div className="panel-content empty-results" role="status" aria-live="polite">
      <h1>Carregando {subject}…</h1>
      <p className="section-description">
        {remote.status === "loading" && remote.slow ? "Conectando à API. O servidor gratuito pode levar até um minuto para acordar na primeira consulta." : "Buscando dados na API do PHAROS."}
      </p>
    </div>
  );
}

export default function Prototype() {
  const params = useSearchParams();
  const move = useViewMotion(params.toString());
  const screen = screenOrder.find((key) => screens[key] === params.get("tela")) ?? "home";
  const [attempt, setAttempt] = useState(0);
  const retry = () => setAttempt((value) => value + 1);
  const stopsRemote = useStops(attempt);
  const stops = useMemo(() => stopsRemote.status === "ok" ? stopsRemote.data : [], [stopsRemote]);
  const [draft, setDraft] = useState<Trip>();
  const [participation, setParticipation] = useState<Participation>({});
  const [reportLocation, setReportLocation] = useState<Category>("dark");
  const [reports, setReports] = useState<PendingReport[]>([]);
  const [reportReceipt, setReportReceipt] = useState<string>();
  const pin = categories.find(({ id }) => id === params.get("pin"))?.id;
  const showPin = pin && screen !== "report";
  const urlTrip = useMemo(() => tripFromParams(params, stops), [params, stops]);
  const trip = screen === "plan" ? draft ?? urlTrip : urlTrip;
  const needsRoutes = (screen === "compare" || screen === "detail" || screen === "report") && stopsRemote.status === "ok" && Boolean(trip.origin && trip.destination);
  const { remote: trajetos, choose } = useTrajetos(needsRoutes ? trip : null, attempt);
  const routes = trajetos.status === "ok" ? trajetos.data.routes : [];
  const route = routes.find(({ id }) => id === params.get("rota")) ?? routes[0];
  const available = trajetos.status !== "ok" || routes.length > 0;
  const routeLetter = route?.id ?? "a";
  const report = reports.find(({ receipt }) => receipt === reportReceipt);
  const returnLabel = {
    home: "Voltar ao mapa",
    plan: "Voltar ao planejamento",
    compare: "Voltar à comparação",
    detail: `Voltar aos detalhes da rota ${routeLetter.toUpperCase()}`,
    report: "Voltar à rota",
  }[screen];
  function go(next: Screen, { query = trip, selected, observation, replace = false }: {
    query?: Trip; selected?: RouteId; observation?: Category; replace?: boolean;
  } = {}) {
    const search = new URLSearchParams();
    if (next !== "home") {
      search.set("tela", screens[next]);
      search.set("origem", query.origin);
      search.set("destino", query.destination);
      search.set("hora", query.time);
      search.set("preferencia", query.preference);
      if (selected) search.set("rota", selected);
    }
    if (observation) search.set("pin", observation);
    const nextQuery = search.toString();
    const href = nextQuery ? `/?${nextQuery}` : "/";
    const changesView = screen !== next || pin !== observation;
    const goesBack = screenOrder.indexOf(next) < screenOrder.indexOf(screen) || Boolean(showPin && !observation);

    move(nextQuery, () => {
      setDraft(next === "plan" ? query : undefined);
      if (replace) {
        window.history.replaceState(null, "", href);
      } else {
        window.history.pushState(null, "", href);
        window.scrollTo(0, 0);
      }
    }, changesView ? (goesBack ? "back" : "forward") : undefined);
  }

  const closePin = () => go(screen, { selected: route?.id, replace: true });
  const openPin = (observation: Category) => go(screen, { selected: route?.id, observation });

  const observationPanel = showPin && (
    <Observation id={pin} choice={participation[pin]}
      onChange={(choice) => setParticipation((previous) => ({ ...previous, [pin]: choice }))}
      onClose={closePin} returnLabel={returnLabel} />
  );

  return (
    <div className={`prototype screen-${screen}${showPin ? " with-pin" : ""}`}>
      <header className="site-header">
        <div className="brand-group">
          {(showPin || screen === "compare" || screen === "report") && (
            <button type="button" className="mobile-only header-back" aria-label="Voltar" onClick={showPin ? closePin : () => screen === "report" ? go("detail", { selected: route?.id }) : go("plan")}><Icon name="back" /></button>
          )}
          <button className="brand" type="button" onClick={() => go("home")} aria-label="PHAROS, início">
            <span className="brand-mark"><img src="/logo.png" alt="" /></span><strong>PHAROS</strong>
          </button>
          <span className="desktop-only brand-region">CAPÃO REDONDO / SP</span>
        </div>
        <button type="button" className="button primary header-cta desktop-only" onClick={() => go("plan")}>Para onde vamos?</button>
        <span className="desktop-only pilot-label"><Icon name="help" /> Piloto ilustrativo</span>
        <span className="mobile-only pilot-label"><Icon name="pin" /> Zona Sul · SP</span>
      </header>
      <div className="demo"><Icon name="flask" />Demonstração · trajetos da API · relatos e mapa simulados</div>
      <main className="workspace">
        <MapView key={screen} mode={screen} trip={trip} stops={stops} routes={routes} selected={screen === "home" || screen === "plan" ? "a" : routeLetter}
          mobileMode={showPin ? "pin" : undefined} participation={participation} available={available}
          onPin={screen === "report" ? setReportLocation : openPin}>
          {screen === "plan" && (
            <aside className="map-message desktop-only">
              <p className="eyebrow">SEU BAIRRO, EM PERSPECTIVA</p>
              <h2>Mais contexto.<br />Melhores escolhas.</h2>
              <p>A mobilidade começa com informação. Compare conexões e leia observações moderadas, sem classificar trajetos por risco.</p>
            </aside>
          )}
          {screen === "compare" && route && (
            <aside className="map-message comparison-message desktop-only">
              <strong><Icon name="route" /> Rota {route.id.toUpperCase()} selecionada · {route.warnings.length} {route.warnings.length === 1 ? "aviso" : "avisos"} (simulados)</strong>
              <p>Pins destacados pertencem ao entorno da rota. Cores indicam participação comunitária, não perigo.</p>
            </aside>
          )}
          {screen === "detail" && route && (
            <>
              <HistoryCard route={route} className="history-on-map desktop-only" />
              <div className="map-legend desktop-only"><Legend /></div>
            </>
          )}
          {observationPanel && <div className="observation-on-map desktop-only">{observationPanel}</div>}
        </MapView>
        {screen !== "home" && (
          <section className="panel">
            <div className="sheet-handle" aria-hidden="true" />
            {stopsRemote.status !== "ok" && <StatusPanel remote={stopsRemote} onRetry={retry} subject="as paradas" />}
            {stopsRemote.status === "ok" && screen === "plan" && <Planning trip={trip} stops={stops} setTrip={setDraft} onBack={() => go("home")} onSubmit={() => go("compare")} />}
            {needsRoutes && trajetos.status !== "ok" && <StatusPanel remote={trajetos} onRetry={retry} subject="os trajetos" />}
            {needsRoutes && trajetos.status === "ok" && routes.length === 0 && (
              <div className="panel-content empty-results">
                <h1>Nenhum trajeto disponível</h1>
                <p className="section-description">{trajetos.data.response.mensagem ?? "Não há trajetos calculados para esse par de paradas neste horário."}</p>
                <button type="button" className="button primary" onClick={() => go("plan")}>Editar origem, destino ou horário</button>
              </div>
            )}
            {screen === "compare" && route && (
              <Comparison trip={trip} stops={stops} routes={routes} route={route} onEdit={() => go("plan")}
                onSort={(preference) => go("compare", { query: { ...trip, preference }, replace: true })}
                onSelect={(selected) => go("compare", { selected, replace: true })}
                onDetails={() => { choose(route.idAlternativa); go("detail", { selected: route.id }); }} />
            )}
            {screen === "detail" && route && (
              <Details trip={trip} stops={stops} route={route} participation={participation} report={report}
                onBack={() => go("compare", { selected: route.id })} onPin={openPin}
                onReport={() => { setReportReceipt(undefined); setReportLocation("dark"); go("report", { selected: route.id }); }} />
            )}
            {screen === "report" && route && (
              <ReportForm route={route.id} location={reportLocation} onLocation={setReportLocation}
                onCancel={() => go("detail", { selected: route.id })}
                onSend={(pending) => {
                  setReports((current) => [...current, pending]);
                  setReportReceipt(pending.receipt);
                  go("detail", { selected: route.id, replace: true });
                }} />
            )}
          </section>
        )}
        {observationPanel && (
          <div className="observation-sheet mobile-only"><div className="sheet-handle" aria-hidden="true" />{observationPanel}</div>
        )}
      </main>
      {!showPin && screen !== "report" && <div className="mobile-action">
        <button type="button" className="button primary" onClick={() => go("plan")}><Icon name="arrow" />Para onde vamos?</button>
      </div>}
    </div>
  );
}
