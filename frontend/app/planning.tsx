import { getStop, preferences, stops, type StopId, type Trip } from "./data";
import { BackButton, Icon, Legend, SectionTitle } from "./ui";

export function Planning({ trip, setTrip, onBack, onSubmit }: {
  trip: Trip;
  setTrip: (trip: Trip) => void;
  onBack: () => void;
  onSubmit: () => void;
}) {
  function chooseStop(key: "origin" | "destination", id: StopId) {
    const other = key === "origin" ? "destination" : "origin";
    setTrip({ ...trip, [key]: id, [other]: trip[other] === id ? trip[key] : trip[other] });
  }

  return (
    <div className="panel-content">
      <BackButton onClick={onBack}>Voltar ao mapa</BackButton>
      <SectionTitle step="01 / PLANEJAR">Para onde vamos?</SectionTitle>
      <p className="section-description">Explore conexões e observações da comunidade antes de sair.</p>
      <form className="plan-form" onSubmit={(event) => { event.preventDefault(); onSubmit(); }}>
        <div className="trip-fields">
          {(["origin", "destination"] as const).map((key) => (
            <label key={key} className="field-line">
              <Icon name={key === "origin" ? "circle-origin" : "pin"} />
              <span>
                <span className="field-label">{key === "origin" ? "Origem" : "Destino"}</span>
                <select value={trip[key]} onChange={(event) => chooseStop(key, event.target.value as StopId)}>
                  {stops.map((stop) => <option key={stop.id} value={stop.id}>{getStop(stop.id).name}</option>)}
                </select>
              </span>
            </label>
          ))}
          <button type="button" className="swap-button" aria-label="Inverter origem e destino" onClick={() => setTrip({ ...trip, origin: trip.destination, destination: trip.origin })}>
            <Icon name="swap" />
          </button>
        </div>
        <label className="field-line time-field">
          <Icon name="clock" />
          <span>
            <span className="field-label">Sair às</span>
            <span className="time-value" aria-hidden="true">08 nov. · {trip.time || "—"}</span>
          </span>
          <input aria-label="Horário de partida" className="time-input" type="time" required value={trip.time} onChange={(event) => setTrip({ ...trip, time: event.target.value })} />
          <Icon name="down" />
        </label>
        <fieldset className="preferences">
          <legend>O que importa no seu trajeto?</legend>
          <div className="preference-options">
            {preferences.map(({ id, name, icon }) => (
              <label key={id} className="preference" data-selected={trip.preference === id}>
                <input type="radio" name="preferencia" checked={trip.preference === id} onChange={() => setTrip({ ...trip, preference: id })} />
                <Icon name={icon} />{name}
              </label>
            ))}
          </div>
        </fieldset>
        <button type="submit" className="button primary"><Icon name="arrow" />Encontrar trajetos</button>
      </form>
      <aside className="territory-note">
        <Icon name="network" />
        <div><strong>Um território, mais contexto.</strong><p>Piloto no Capão Redondo, Zona Sul de São Paulo. Busca restrita às conexões previamente cadastradas nesta demonstração.</p></div>
      </aside>
      <p className="fine-print">Itinerários, linhas e locais aproximados são simulados. O horário informa a partida de referência. Os tempos do percurso são fixos na demonstração.</p>
      <div className="desktop-only"><Legend /></div>
    </div>
  );
}
