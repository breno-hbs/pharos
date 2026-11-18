"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { categories, hasMockConnection, orderedRoutes, routes, tripFromParams, type Category, type Participation, type PendingReport, type RouteId, type Trip } from "./data";
import { MapView } from "./map";
import { Observation, ReportForm } from "./observations";
import { Planning } from "./planning";
import { Comparison, Details, HistoryCard } from "./routes";
import { Icon, Legend } from "./ui";

const screens = {
  home: "",
  plan: "planejamento",
  compare: "comparacao",
  detail: "detalhes",
  report: "observacao",
} as const;
type Screen = keyof typeof screens;

export default function Prototype() {
  const params = useSearchParams();
  const screen = (Object.keys(screens) as Screen[]).find((key) => screens[key] === params.get("tela")) ?? "home";
  const [draft, setDraft] = useState(() => tripFromParams(params));
  const [participation, setParticipation] = useState<Participation>({});
  const [reportLocation, setReportLocation] = useState<Category>("dark");
  const [reports, setReports] = useState<PendingReport[]>([]);
  const [reportReceipt, setReportReceipt] = useState<string>();
  const pin = categories.find(({ id }) => id === params.get("pin"))?.id;
  const showPin = pin && screen !== "report";
  const trip = screen === "plan" ? draft : tripFromParams(params);
  const route = routes.find(({ id }) => id === params.get("rota")) ?? orderedRoutes(trip.preference)[0];
  const available = hasMockConnection(trip);
  const report = reports.find(({ receipt }) => receipt === reportReceipt);
  const returnLabel = {
    home: "Voltar ao mapa",
    plan: "Voltar ao planejamento",
    compare: "Voltar à comparação",
    detail: `Voltar aos detalhes da rota ${route.id.toUpperCase()}`,
    report: "Voltar à rota",
  }[screen];
  function go(next: Screen, { query = trip, selected, observation, replace = false }: {
    query?: Trip; selected?: RouteId; observation?: Category; replace?: boolean;
  } = {}) {
    const search = new URLSearchParams();
    if (next !== "home") {
      search.set("tela", screens[next]);
      search.set("origem", query.origin);
      search.set("hora", query.time);
      search.set("preferencia", query.preference);
      if (selected) search.set("rota", selected);
    }
    if (observation) search.set("pin", observation);
    if (next === "plan") setDraft(query);
    const href = search.size ? `/?${search}` : "/";
    if (replace) {
      window.history.replaceState(null, "", href);
    } else {
      window.history.pushState(null, "", href);
      window.scrollTo(0, 0);
    }
  }

  const closePin = () => go(screen, { selected: route.id, replace: true });
  const openPin = (observation: Category) => go(screen, { selected: route.id, observation });

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
            <button type="button" className="mobile-only header-back" aria-label="Voltar" onClick={showPin ? closePin : () => screen === "report" ? go("detail", { selected: route.id }) : go("plan")}><Icon name="back" /></button>
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
      <div className="demo"><Icon name="flask" />Demonstração · dados simulados</div>
      <main className="workspace">
        <MapView key={screen} mode={screen} trip={trip} selected={screen === "home" || screen === "plan" ? "a" : route.id}
          mobileMode={showPin ? "pin" : undefined} participation={participation} available={available}
          onPin={screen === "report" ? setReportLocation : openPin}>
          {screen === "plan" && (
            <aside className="map-message desktop-only">
              <p className="eyebrow">SEU BAIRRO, EM PERSPECTIVA</p>
              <h2>Mais contexto.<br />Melhores escolhas.</h2>
              <p>A mobilidade começa com informação. Compare conexões e leia observações moderadas, sem classificar trajetos por risco.</p>
            </aside>
          )}
          {screen === "compare" && available && (
            <aside className="map-message comparison-message desktop-only">
              <strong><Icon name="route" /> Rota {route.id.toUpperCase()} selecionada · {route.warnings.length} {route.warnings.length === 1 ? "aviso" : "avisos"}</strong>
              <p>Pins destacados pertencem ao entorno da rota. Cores indicam participação comunitária, não perigo.</p>
            </aside>
          )}
          {screen === "detail" && available && (
            <>
              <HistoryCard className="history-on-map desktop-only" />
              <div className="map-legend desktop-only"><Legend /></div>
            </>
          )}
          {observationPanel && <div className="observation-on-map desktop-only">{observationPanel}</div>}
        </MapView>
        {screen !== "home" && (
          <section className="panel">
            <div className="sheet-handle" aria-hidden="true" />
            {screen === "plan" && <Planning trip={trip} setTrip={setDraft} onBack={() => go("home")} onSubmit={() => go("compare")} />}
            {!available && screen !== "plan" && (
              <div className="panel-content empty-results">
                <h1>Nenhum trajeto disponível</h1>
                <p className="section-description">A demonstração não tem uma conexão cadastrada nesse sentido.</p>
                <button type="button" className="button primary" onClick={() => go("plan")}>Editar origem e destino</button>
              </div>
            )}
            {screen === "compare" && available && (
              <Comparison trip={trip} route={route} onEdit={() => go("plan")}
                onSort={(preference) => go("compare", { query: { ...trip, preference }, selected: orderedRoutes(preference)[0].id, replace: true })}
                onSelect={(selected) => go("compare", { selected, replace: true })}
                onDetails={() => go("detail", { selected: route.id })} />
            )}
            {screen === "detail" && available && (
              <Details trip={trip} route={route} participation={participation} report={report}
                onBack={() => go("compare", { selected: route.id })} onPin={openPin}
                onReport={() => { setReportReceipt(undefined); setReportLocation("dark"); go("report", { selected: route.id }); }} />
            )}
            {screen === "report" && available && (
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
