"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { defaultTrip } from "./data";
import { MapView } from "./map";
import { Planning } from "./planning";
import { Icon } from "./ui";

export default function Prototype() {
  const params = useSearchParams();
  const screen = params.get("tela") === "planejamento" ? "plan" : "home";
  const [trip, setTrip] = useState(defaultTrip);

  function go(next: "home" | "plan") {
    window.history.pushState(null, "", next === "home" ? "/" : "/?tela=planejamento");
    window.scrollTo(0, 0);
  }

  return (
    <div className={`prototype screen-${screen}`}>
      <header className="site-header">
        <div className="brand-group">
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
        <MapView key={screen} mode={screen} trip={trip}>
          {screen === "plan" && (
            <aside className="map-message desktop-only">
              <p className="eyebrow">SEU BAIRRO, EM PERSPECTIVA</p>
              <h2>Mais contexto.<br />Melhores escolhas.</h2>
              <p>A mobilidade começa com informação. Compare conexões e leia observações moderadas, sem classificar trajetos por risco.</p>
            </aside>
          )}
        </MapView>
        {screen === "plan" && (
          <section className="panel" aria-label="Planejamento">
            <div className="sheet-handle" aria-hidden="true" />
            <Planning trip={trip} setTrip={setTrip} onBack={() => go("home")} onSubmit={() => go("plan")} />
          </section>
        )}
      </main>
      <div className="mobile-action">
        <button type="button" className="button primary" onClick={() => go("plan")}><Icon name="arrow" />Para onde vamos?</button>
      </div>
    </div>
  );
}
