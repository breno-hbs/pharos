import { useLayoutEffect, useRef } from "react";
import { categories, findStop, observations, offsetTime, preferences, type Category, type Participation, type PendingReport, type Preference, type Route, type Stop, type Trip } from "./data";
import { BackButton, Icon, Legend, SectionTitle } from "./ui";

function occurrenceCount(route: Route) {
  const count = route.occurrences;
  return count === 1 ? "1 registro histórico" : `${count} registros históricos`;
}

function warningCount(route: Route) {
  const count = route.warnings.length;
  return count === 1 ? "1 aviso próximo" : `${count} avisos próximos`;
}

export function Comparison({ trip, stops, routes, route, onEdit, onSort, onSelect, onDetails }: {
  trip: Trip;
  stops: readonly Stop[];
  routes: readonly Route[];
  route: Route;
  onEdit: () => void;
  onSort: (preference: Preference) => void;
  onSelect: (id: Route["id"]) => void;
  onDetails: () => void;
}) {
  const optionsRef = useRef<HTMLFieldSetElement>(null);
  const previousPositions = useRef(new Map<Element, number>());
  const reorderAnimations = useRef(new WeakMap<Element, Animation>());

  function sort(preference: Preference) {
    const cards = optionsRef.current?.children;
    if (cards && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      previousPositions.current = new Map(Array.from(cards, (card) => [card, card.getBoundingClientRect().top]));
    }
    onSort(preference);
  }

  useLayoutEffect(() => {
    for (const [card, previousTop] of previousPositions.current) {
      reorderAnimations.current.get(card)?.cancel();
      const distance = previousTop - card.getBoundingClientRect().top;
      if (distance !== 0) {
        const animation = card.animate(
          [{ transform: `translateY(${distance}px)` }, { transform: "translateY(0)" }],
          { duration: 240, easing: "cubic-bezier(.2, .75, .25, 1)" },
        );
        reorderAnimations.current.set(card, animation);
      }
    }
    previousPositions.current.clear();
  }, [trip.preference]);

  return (
    <div className="panel-content comparison">
      <BackButton onClick={onEdit}>Voltar ao planejamento</BackButton>
      <SectionTitle step="02 / COMPARAR">{routes.length === 1 ? "Uma forma de chegar." : `${routes.length === 2 ? "Duas" : "Três"} formas de chegar.`}</SectionTitle>
      <button type="button" className="trip-summary" onClick={onEdit} aria-label="Editar origem e destino">
        <Icon name="swap" />
        <span>{findStop(stops, trip.origin).name}<strong>{findStop(stops, trip.destination).name}</strong></span>
        <Icon name="pencil" />
      </button>
      <div className="comparison-meta">
        <span>Dia útil · {trip.time}</span>
        <select aria-label="Ordenar trajetos" value={trip.preference} onChange={(event) => sort(event.target.value as Preference)}>
          {preferences.map(({ id, name }) => <option key={id} value={id}>{name}</option>)}
        </select>
      </div>
      <p className="comparison-help">Ícones = relatos por categoria. Ordem: confirmações.</p>
      <fieldset ref={optionsRef} className="route-options" aria-label="Escolha um trajeto">
        {routes.map((item) => {
          const selected = route.id === item.id;
          return (
            <label key={item.id} className={`route-card route-option-${item.id}`} data-selected={selected}>
              <input type="radio" name="rota" checked={selected} onChange={() => onSelect(item.id)} />
              <span className="route-card-top">
                <span className="route-stamp">{item.id.toUpperCase()}</span><strong>{item.caption}</strong>
                <span className="route-warnings">
                  {categories.filter(({ id }) => (item.warnings as readonly Category[]).includes(id)).sort((a, b) => observations[b.id].count - observations[a.id].count).map(({ id, label, icon }) => (
                    <span key={id} title={label} aria-label={`1 relato: ${label}`} data-category={id}><Icon name={icon} tinted />1</span>
                  ))}
                </span>
                <span className="route-radio" aria-hidden="true">{selected ? "✓" : ""}</span>
              </span>
              {item.fewestTransfers && item.caption !== "Menos baldeações" && <span className="route-extra">Também: menos baldeações</span>}
              <span className="route-card-main">
                <span className="route-duration">{item.minutes} min</span>
                <span><strong>Ônibus {item.lines.join(" + ")}</strong><small>{item.distanceKm.toFixed(1).replace(".", ",")} km · {item.transfers} {item.transfers === 1 ? "baldeação" : "baldeações"}</small></span>
              </span>
              <span className="route-card-bottom"><span><Icon name="bus" /> {item.steps.length} {item.steps.length === 1 ? "trecho" : "trechos"} de ônibus</span><span>{occurrenceCount(item)}</span></span>
              {selected && <span className="route-card-selected mobile-only">Selecionada · {trip.time} → {offsetTime(trip.time, item.minutes)} <span aria-hidden="true">→</span></span>}
            </label>
          );
        })}
      </fieldset>
      <button type="button" className="button primary" onClick={onDetails}><Icon name="arrow" />Ver detalhes da rota {route.id.toUpperCase()}</button>
      <Legend />
      <p className="fine-print">Tempos, distâncias e linhas vêm da API (horários programados, não tempo real). Os ícones de relatos são simulados. Nenhuma contagem é medida de risco nem recomendação de segurança.</p>
    </div>
  );
}

export function HistoryCard({ route, className = "" }: { route: Route; className?: string }) {
  const simulated = route.indicators.some(({ simulado }) => simulado);
  const sources = [...new Set(route.indicators.map(({ nmFonte }) => nmFonte))];
  return (
    <aside className={`history-card ${className}`}>
      <div className="history-title"><h2>Contexto histórico</h2><span>{simulated ? "VALORES SIMULADOS" : "DADOS OFICIAIS"}</span></div>
      {route.indicators.length ? (
        <>
          <p>{route.occurrences} {route.occurrences === 1 ? "registro agregado" : "registros agregados"} nas proximidades da rota {route.id.toUpperCase()}. Sem associação a pessoas, endereços ou previsões.</p>
          <ul className="history-list">
            {route.indicators.map((item) => (
              <li key={item.idIndicador}><strong>{item.qtOcorrencias}</strong> {item.nmTipo.toLowerCase()} <small>· {item.nrAno} · raio de {item.nrRaioM} m · {item.tpFaixaHoraria.toLowerCase()}</small></li>
            ))}
          </ul>
        </>
      ) : <p>Esta rota ainda não tem indicadores históricos cadastrados.</p>}
      {sources.length > 0 && <p className="history-period">Fonte: {sources.join("; ")}.{simulated ? " Os valores marcados como simulados são ilustrativos e não descrevem ocorrências reais." : ""}</p>}
      <p>Contagem histórica agregada, não é previsão de risco nem garantia de segurança.</p>
    </aside>
  );
}

export function Details({ trip, stops, route, participation, report, onBack, onPin, onReport }: {
  trip: Trip;
  stops: readonly Stop[];
  route: Route;
  participation: Participation;
  report?: PendingReport;
  onBack: () => void;
  onPin: (category: Category) => void;
  onReport: () => void;
}) {
  const origin = findStop(stops, trip.origin);
  const destination = findStop(stops, trip.destination);
  const steps = route.steps.flatMap((step, index) => {
    const items: { title: string; path: string; duration: string; icon: string; warning?: Category }[] = [];
    if (index > 0) items.push({ title: "Baldeação na mesma parada", path: step.nmParadaEmbarque, duration: "troca de linha sem caminhada", icon: "repeat" });
    items.push({ title: `Ônibus ${step.cdLinha}`, path: `${step.nmParadaEmbarque} → ${step.nmParadaDesembarque}`, duration: index === 0 ? `embarque em ${origin.short}` : "segue até o destino", icon: "bus", warning: route.warnings[index] });
    return items;
  });
  const letter = route.id.toUpperCase();
  const km = route.distanceKm.toFixed(1).replace(".", ",");
  return (
    <div className="panel-content details">
      <BackButton onClick={onBack}>Voltar à comparação</BackButton>
      <SectionTitle step={`03 / DETALHES · ROTA ${letter}`}>Seu trajeto, por etapas.</SectionTitle>
      <div className="detail-summary">
        <div><span className="route-duration">{route.minutes} min</span><span><strong>{trip.time} → {offsetTime(trip.time, route.minutes)}</strong><small>Ônibus {route.lines.join(" + ")}</small></span></div>
        <ul><li>{km} km</li><li>{route.transfers} {route.transfers === 1 ? "baldeação" : "baldeações"}</li><li>{occurrenceCount(route)}</li></ul>
        <p>HORÁRIOS PROGRAMADOS · ESTIMATIVA, NÃO TEMPO REAL</p>
      </div>
      <ol className="timeline">
        {steps.map((step, index) => {
          const category = categories.find(({ id }) => id === step.warning);
          return (
            <li key={`${step.title}-${index}`}>
              <span className="step-icon"><Icon name={step.icon} /></span>
              <div>
                <div className="timeline-title"><h2>{step.title}</h2></div>
                <p>{step.path}</p><p className="step-duration">{step.duration}</p>
                {category && (
                  <button type="button" className="step-warning" data-category={category.id} onClick={() => onPin(category.id)}>
                    <Icon name={category.icon} tinted />{category.label} · 1 aviso próximo (simulado) · {observations[category.id].count + Number(participation[category.id] === "confirmed")} confirmações
                  </button>
                )}
              </div>
            </li>
          );
        })}
        <li className="arrival">
          <Icon name="flag" />
          <div><h2>{destination.name}</h2><p>{offsetTime(trip.time, route.minutes)} · chegada estimada</p></div>
        </li>
      </ol>
      <HistoryCard route={route} className="mobile-only" />
      <section className="route-voices" aria-label="Vozes do percurso">
        <div className="voices-title"><h2>Vozes do percurso</h2><span>Moderados</span></div>
        {[...route.warnings].sort((a, b) => observations[b].count - observations[a].count).slice(0, 2).reverse().map((id) => {
          const category = categories.find((item) => item.id === id)!;
          const observation = observations[id];
          return (
            <button type="button" key={id} className="voice-card" data-category={id} onClick={() => onPin(id)}>
              <span><Icon name={category.icon} tinted /><strong>{category.label}</strong> <small>RELATO SIMULADO</small></span>
              <p>{observation.description}</p><small>{observation.date} · {observation.count + Number(participation[id] === "confirmed")} confirmações</small>
            </button>
          );
        })}
      </section>
      {report && (
        <div className="feedback" role="status">
          <Icon name="check" tinted /><div><strong>Observação enviada</strong>
            <p>Recibo <b>{report.receipt}</b> · {report.status.toLowerCase()} de moderação. Envio simulado.</p>
          </div>
        </div>
      )}
      <button type="button" className="button primary" onClick={onReport}><Icon name="plus" tinted />Adicionar observação</button>
      <div className="mobile-only"><Legend /></div>
      <p className="fine-print">Informações para apoiar decisões, não para prever crimes ou garantir segurança. Confira condições e serviços por outros meios.</p>
    </div>
  );
}
