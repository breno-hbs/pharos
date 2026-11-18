import { useState } from "react";
import { categories, observations, participationBand, type Category, type Participation, type RouteId } from "./data";
import { BackButton, Icon, Legend, SectionTitle } from "./ui";

export function Observation({ id, choice, onChange, onClose, returnLabel }: {
  id: Category;
  choice?: Participation[Category];
  onChange: (choice?: Participation[Category]) => void;
  onClose: () => void;
  returnLabel: string;
}) {
  const category = categories.find((item) => item.id === id)!;
  const observation = observations[id];
  const confirmed = choice === "confirmed";
  const contested = choice === "contested";
  const count = observation.count + Number(confirmed);
  const band = participationBand(count);
  const bandLabel = { low: "0–4 · participação inicial", medium: "5–14 · participação intermediária", high: "15+ · participação alta" }[band];

  return (
    <section className={`observation observation-${band}`} aria-labelledby="observation-title">
      {choice && (
        <div className="feedback" role="status">
          <Icon name="check" />
          <div><strong>{confirmed ? "Confirmação registrada" : "Contestação registrada"}</strong>
            <p>{confirmed ? `${observation.count} → ${count} confirmações. O pin está na faixa ${bandLabel}.` : "Sua contestação foi registrada na demonstração."}</p>
          </div>
        </div>
      )}
      <div className="observation-top">
        <span><Icon name={category.icon} />{category.label}</span>
        <button type="button" className="icon-button" onClick={onClose} aria-label="Fechar observação"><Icon name="close" /></button>
      </div>
      <h1 id="observation-title">{observation.place}</h1>
      <p className="observation-location">{observation.nearby} · local aproximado</p>
      <div className="reported-note">
        <strong>RELATO SIMULADO · MODERADO</strong>
        <p>“{observation.description}”</p>
        <small>{observation.date} · autoria preservada</small>
      </div>
      <div className="participation-summary">
        <span className={band}>{count}</span>
        <div><strong>confirmações da comunidade</strong><p>Faixa {bandLabel}{confirmed ? " · inclui a sua confirmação" : ""}</p></div>
      </div>
      <p className="fine-print">{contested ? "1 contestação" : "0 contestações"} · relato comunitário simulado</p>
      <div className="observation-actions">
        <button type="button" className="button primary" aria-pressed={confirmed} onClick={() => onChange(confirmed ? undefined : "confirmed")}>
          <Icon name={confirmed ? "check" : "plus"} />{confirmed ? "Confirmado" : "Confirmar"}
        </button>
        <button type="button" className="button secondary" aria-pressed={contested} onClick={() => onChange(contested ? undefined : "contested")}>
          <Icon name={contested ? "check" : "plus"} />{contested ? "Contestado" : "Contestar"}
        </button>
      </div>
      {choice && <div className="undo-line"><span>Você pode retirar sua {confirmed ? "confirmação" : "contestação"}.</span><button type="button" onClick={() => onChange()}>Desfazer</button></div>}
      <p className="fine-print">Confirme apenas se você também observou a situação. As confirmações não verificam nem preveem ocorrências.</p>
      <div className="mobile-only observation-footer"><Legend /><BackButton onClick={onClose}>{returnLabel}</BackButton></div>
    </section>
  );
}

export function ReportForm({ route, location, onLocation, onCancel, onSend }: {
  route: RouteId;
  location: Category;
  onLocation: (location: Category) => void;
  onCancel: () => void;
  onSend: () => void;
}) {
  const [category, setCategory] = useState<Category>("dark");
  const [description, setDescription] = useState("");
  const [editingLocation, setEditingLocation] = useState(false);
  const observation = observations[location];
  return (
    <div className="panel-content report">
      <SectionTitle step={`CONTRIBUIR / ROTA ${route.toUpperCase()}`}>O que você observou?</SectionTitle>
      <p className="section-description">Compartilhe o contexto do lugar. Sua observação passa por moderação antes de aparecer no mapa.</p>
      <form onSubmit={(event) => { event.preventDefault(); if (description.trim()) onSend(); }}>
        <fieldset className="report-categories">
          <legend>Categoria *</legend>
          <div>
            {categories.map(({ id, label, icon }) => (
              <label key={id} className="report-category" data-selected={category === id}>
                <input type="radio" name="categoria" value={id} checked={category === id} onChange={() => setCategory(id)} />
                <Icon name={icon} />{label}
              </label>
            ))}
          </div>
        </fieldset>
        <div>
          <p className="report-label">Localização aproximada *</p>
          {editingLocation ? (
            <select className="report-location-select" aria-label="Localização aproximada" value={location} onChange={(event) => {
              onLocation(event.target.value as Category);
              setEditingLocation(false);
            }} onBlur={() => setEditingLocation(false)} autoFocus>
              {categories.map(({ id }) => <option key={id} value={id}>{observations[id].place}</option>)}
            </select>
          ) : (
            <button type="button" className="report-location" onClick={() => setEditingLocation(true)}>
              <Icon name="pin" /><span>{observation.place}<small>{observation.nearby}</small></span><Icon name="pencil" />
            </button>
          )}
          <p className="fine-print">Local ilustrativo selecionado no mapa. Evite informar números de imóveis ou endereços pessoais.</p>
        </div>
        <label>
          <span className="report-label">Descrição * <small>Até 500 caracteres</small></span>
          <span className="description-box">
            <textarea
              placeholder="Luminária apagada no trecho da calçada próximo ao ponto, observada hoje ao anoitecer."
              value={description} onChange={(event) => setDescription(event.target.value)} required maxLength={500}
            />
            <small>CONTEÚDO DEMONSTRATIVO SIMULADO</small>
          </span>
        </label>
        <p className="report-guidance fine-print"><Icon name="shield" />Descreva o que observou, sem identificar pessoas, fazer acusações ou prever ocorrências. Este canal não atende emergências.</p>
        <button type="submit" className="button primary" disabled={!description.trim()}><Icon name="send" />Enviar</button>
        <button type="button" className="cancel-report" onClick={onCancel}>Cancelar e voltar à rota</button>
      </form>
    </div>
  );
}
