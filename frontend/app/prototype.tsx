"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { orderedRoutes, routes, tripFromParams, type RouteId, type Trip } from "./data";
import { MapView } from "./map";
import { Planning } from "./planning";
import { Comparison, Details, HistoryCard } from "./routes";
import { Icon, Legend } from "./ui";

const screens = {
  home: "",
  plan: "planejamento",
  compare: "comparacao",
  detail: "detalhes",
} as const;
type Screen = keyof typeof screens;

export default function Prototype() {
  const params = useSearchParams();
  const screen = (Object.keys(screens) as Screen[]).find((key) => screens[key] === params.get("tela")) ?? "home";
  const [draft, setDraft] = useState(() => tripFromParams(params));
  const trip = screen === "plan" ? draft : tripFromParams(params);
  const route = routes.find(({ id }) => id === params.get("rota")) ?? orderedRoutes(trip.preference)[0];

  function go(next: Screen, { query = trip, selected, replace = false }: {
    query?: Trip; selected?: RouteId; replace?: boolean;
  } = {}) {
    const search = new URLSearchParams();
    if (next !== "home") {
      search.set("tela", screens[next]);
      search.set("origem", query.origin);
      search.set("hora", query.time);
      search.set("preferencia", query.preference);
      if (selected) search.set("rota", selected);
    }
    if (next === "plan") setDraft(query);
    const href = search.size ? `/?${search}` : "/";
    if (replace) {
      window.history.replaceState(null, "", href);
    } else {
      window.history.pushState(null, "", href);
      window.scrollTo(0, 0);
    }
  }

  return (
    <div className={`prototype screen-${screen}`}>
      <header className="site-header">
        <div className="brand-group">
          {screen === "compare" && <button type="button" className="mobile-only header-back" aria-label="Voltar ao planejamento" onClick={() => go("plan")}><Icon name="back" /></button>}
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
        <MapView key={screen} mode={screen} trip={trip} selected={screen === "compare" || screen === "detail" ? route.id : "a"}>
          {screen === "plan" && (
            <aside className="map-message desktop-only">
              <p className="eyebrow">SEU BAIRRO, EM PERSPECTIVA</p>
              <h2>Mais contexto.<br />Melhores escolhas.</h2>
              <p>A mobilidade começa com informação. Compare conexões e leia observações moderadas, sem classificar trajetos por risco.</p>
            </aside>
          )}
          {screen === "compare" && (
            <aside className="map-message comparison-message desktop-only">
              <strong><Icon name="route" /> Rota {route.id.toUpperCase()} selecionada · {route.warnings.length} {route.warnings.length === 1 ? "aviso" : "avisos"}</strong>
              <p>Pins destacados pertencem ao entorno da rota. Cores indicam participação comunitária, não perigo.</p>
            </aside>
          )}
          {screen === "detail" && (
            <>
              <HistoryCard className="history-on-map desktop-only" />
              <div className="map-legend desktop-only"><Legend /></div>
            </>
          )}
        </MapView>
        {screen !== "home" && (
          <section className="panel">
            <div className="sheet-handle" aria-hidden="true" />
            {screen === "plan" && <Planning trip={trip} setTrip={setDraft} onBack={() => go("home")} onSubmit={() => go("compare")} />}
            {screen === "compare" && (
              <Comparison trip={trip} route={route} onEdit={() => go("plan")}
                onSort={(preference) => go("compare", { query: { ...trip, preference }, selected: orderedRoutes(preference)[0].id, replace: true })}
                onSelect={(selected) => go("compare", { selected, replace: true })}
                onDetails={() => go("detail", { selected: route.id })} />
            )}
            {screen === "detail" && <Details trip={trip} route={route} onBack={() => go("compare", { selected: route.id })} />}
          </section>
        )}
      </main>
      <div className="mobile-action">
        <button type="button" className="button primary" onClick={() => go("plan")}><Icon name="arrow" />Para onde vamos?</button>
      </div>
    </div>
  );
}
