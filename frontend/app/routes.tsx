import { categories, getStop, observations, offsetTime, orderedRoutes, preferences, type Category, type Participation, type Preference, type Route, type Trip } from "./data";
import { BackButton, Icon, Legend, SectionTitle } from "./ui";

function warningCount(route: Route) {
  const count = route.warnings.length;
  return count === 1 ? "1 aviso próximo" : `${count} avisos próximos`;
}

export function Comparison({ trip, route, onEdit, onSort, onSelect, onDetails }: {
  trip: Trip;
  route: Route;
  onEdit: () => void;
  onSort: (preference: Preference) => void;
  onSelect: (id: Route["id"]) => void;
  onDetails: () => void;
}) {
  return (
    <div className="panel-content comparison">
      <BackButton onClick={onEdit}>Voltar ao planejamento</BackButton>
      <SectionTitle step="02 / COMPARAR">Três formas de chegar.</SectionTitle>
      <button type="button" className="trip-summary" onClick={onEdit} aria-label="Editar origem e destino">
        <Icon name="swap" />
        <span>{getStop(trip.origin).name}<strong>{getStop(trip.destination).name}</strong></span>
        <Icon name="pencil" />
      </button>
      <div className="comparison-meta">
        <span>Hoje · {trip.time}</span>
        <select aria-label="Ordenar trajetos" value={trip.preference} onChange={(event) => onSort(event.target.value as Preference)}>
          {preferences.map(({ id, name }) => <option key={id} value={id}>{name}</option>)}
        </select>
      </div>
      <p className="comparison-help">Ícones = relatos por categoria. Ordem: confirmações.</p>
      <fieldset className="route-options" aria-label="Escolha um trajeto">
        {orderedRoutes(trip.preference).map((item) => {
          const selected = route.id === item.id;
          return (
            <label key={item.id} className={`route-card route-option-${item.id}`} data-selected={selected}>
              <input type="radio" name="rota" checked={selected} onChange={() => onSelect(item.id)} />
              <span className="route-card-top">
                <span className="route-stamp">{item.id.toUpperCase()}</span><strong>{item.caption}</strong>
                <span className="route-warnings">
                  {categories.filter(({ id }) => (item.warnings as readonly Category[]).includes(id)).sort((a, b) => observations[b.id].count - observations[a.id].count).map(({ id, label, icon }) => (
                    <span key={id} title={label} aria-label={`1 relato: ${label}`} data-category={id}><Icon name={icon} />1</span>
                  ))}
                </span>
                <span className="route-radio" aria-hidden="true">{selected ? "✓" : ""}</span>
              </span>
              {item.id === "a" && <span className="route-extra">Também: menos baldeações</span>}
              <span className="route-card-main">
                <span className="route-duration">{item.minutes} min</span>
                <span><strong>Via {item.via}</strong><small>{item.walking} min a pé · {item.transfers} {item.transfers === 1 ? "baldeação" : "baldeações"}</small></span>
              </span>
              <span className="route-card-bottom"><span><Icon name="bus" /> Ônibus {item.lines.join(" + ")}</span><span>{warningCount(item)}</span></span>
              {selected && <span className="route-card-selected mobile-only">Selecionada · {trip.time} → {offsetTime(trip.time, item.minutes)} <span aria-hidden="true">→</span></span>}
            </label>
          );
        })}
      </fieldset>
      <button type="button" className="button primary" onClick={onDetails}><Icon name="arrow" />Ver detalhes da rota {route.id.toUpperCase()}</button>
      <Legend />
      <p className="fine-print">Tempos, linhas e avisos simulados. A quantidade de avisos não é uma medida de risco nem uma recomendação de segurança.</p>
    </div>
  );
}

export function HistoryCard({ className = "" }: { className?: string }) {
  return (
    <aside className={`history-card ${className}`}>
      <div className="history-title"><h2>Contexto histórico</h2><span>EXEMPLO SIMULADO</span></div>
      <p>12 registros fictícios agregados no setor piloto. Sem associação a pessoas, endereços ou previsões.</p>
      <div className="history-bars" aria-label="Registros simulados: julho 3, agosto 5, setembro 4">
        {[["Jul", 3], ["Ago", 5], ["Set", 4]].map(([month, count]) => (
          <div key={month}><span>{count}</span><i style={{ height: Number(count) * 6 }} /><span>{month}</span></div>
        ))}
      </div>
      <p className="history-period">Período ilustrativo: jul.–set. 2026. Todos os valores acima são simulados.</p>
      <p>Fonte oficial de referência: SSP-SP, estatísticas públicas. Os valores deste exemplo NÃO foram extraídos dessa fonte e não descrevem ocorrências reais.</p>
    </aside>
  );
}

export function Details({ trip, route, participation, reportSent, onBack, onPin, onReport }: {
  trip: Trip;
  route: Route;
  participation: Participation;
  reportSent: boolean;
  onBack: () => void;
  onPin: (category: Category) => void;
  onReport: () => void;
}) {
  const walkTo = Math.floor(route.walking / 2);
  const walkFrom = route.walking - walkTo;
  const busTime = route.minutes - route.walking;
  const origin = getStop(trip.origin);
  const destination = getStop(trip.destination);
  const steps = [
    { title: "Caminhe até o ponto", path: `${origin.name} → ${route.short}`, duration: `${walkTo} min · ${walkTo * 70} m`, offset: 0, icon: "walk" },
    { title: `Ônibus ${route.lines.join(" + ")}`, path: `Ponto ${route.short} → conexão Capão Redondo`, duration: `${busTime} min · ${route.transfers ? "1 baldeação" : `sentido ${destination.id === "metro" ? "metrô" : "Jd. Comercial"}`}`, offset: walkTo, icon: "bus" },
    { title: destination.id === "metro" ? "Caminhe até a estação" : "Caminhe até o destino", path: `Conexão → ${destination.name}`, duration: `${walkFrom} min · ${walkFrom * 65} m`, offset: walkTo + busTime, icon: "walk" },
  ];
  const letter = route.id.toUpperCase();
  return (
    <div className="panel-content details">
      <BackButton onClick={onBack}>Voltar à comparação</BackButton>
      <SectionTitle step={`03 / DETALHES · ROTA ${letter}`}>Seu trajeto, por etapas.</SectionTitle>
      <div className="detail-summary">
        <div><span className="route-duration">{route.minutes} min</span><span><strong>{trip.time} → {offsetTime(trip.time, route.minutes)}</strong><small>Via {route.short}</small></span></div>
        <ul><li>{route.walking} min a pé</li><li>{route.transfers} {route.transfers === 1 ? "baldeação" : "baldeações"}</li><li>{warningCount(route)}</li></ul>
        <p>ITINERÁRIO E TEMPOS SIMULADOS</p>
      </div>
      <ol className="timeline">
        {steps.map((step, i) => {
          const category = categories.find(({ id }) => id === route.warnings[i]);
          return (
            <li key={step.title}>
              <span className="step-icon"><Icon name={step.icon} /></span>
              <div>
                <div className="timeline-title"><h2>{step.title}</h2><time>{offsetTime(trip.time, step.offset)}</time></div>
                <p>{step.path}</p><p className="step-duration">{step.duration}</p>
                {category && (
                  <button type="button" className="step-warning" onClick={() => onPin(category.id)}>
                    <Icon name={category.icon} />{category.label} · 1 aviso próximo · {observations[category.id].count + Number(participation[category.id] === "confirmed")} confirmações
                  </button>
                )}
              </div>
            </li>
          );
        })}
        <li className="arrival">
          <Icon name="flag" />
          <div><h2>{destination.name}</h2><p>{offsetTime(trip.time, route.minutes)} · chegada ilustrativa</p></div>
        </li>
      </ol>
      <HistoryCard className="mobile-only" />
      <section className="route-voices" aria-label="Vozes do percurso">
        <div className="voices-title"><h2>Vozes do percurso</h2><span>Moderados</span></div>
        {[...route.warnings].sort((a, b) => observations[b].count - observations[a].count).slice(0, 2).reverse().map((id) => {
          const category = categories.find((item) => item.id === id)!;
          const observation = observations[id];
          return (
            <button type="button" key={id} className="voice-card" onClick={() => onPin(id)}>
              <span><Icon name={category.icon} /><strong>{category.label}</strong> <small>RELATO SIMULADO</small></span>
              <p>{observation.description}</p><small>{observation.date} · {observation.count + Number(participation[id] === "confirmed")} confirmações</small>
            </button>
          );
        })}
      </section>
      {reportSent && <div className="feedback" role="status"><Icon name="check" /><div><strong>Observação enviada</strong><p>Envio simulado. Seu relato aguarda moderação na demonstração.</p></div></div>}
      <button type="button" className="button primary" onClick={onReport}><Icon name="plus" />Adicionar observação</button>
      <div className="mobile-only"><Legend /></div>
      <p className="fine-print">Informações para apoiar decisões, não para prever crimes ou garantir segurança. Confira condições e serviços por outros meios.</p>
    </div>
  );
}
