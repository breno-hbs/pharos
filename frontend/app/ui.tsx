import type { ReactNode } from "react";

export function Icon({ name, tinted = false }: { name: string; tinted?: boolean }) {
  if (tinted) {
    return <span className="icon tinted-icon" style={{ maskImage: `url("/${name}.svg")` }} aria-hidden="true" />;
  }
  return <img className="icon" src={`/${name}.svg`} alt="" aria-hidden="true" />;
}

export function BackButton({ onClick, children }: { onClick: () => void; children: ReactNode }) {
  return <button type="button" className="back-button" onClick={onClick}><span aria-hidden="true">←</span> {children}</button>;
}

export function SectionTitle({ step, children }: { step: string; children: ReactNode }) {
  return <div className="section-title"><p className="eyebrow">{step}</p><h1>{children}</h1></div>;
}

export function Legend({ compact = false }: { compact?: boolean }) {
  return (
    <aside className="legend" aria-label="Legenda de participação">
      <div className="legend-scale">
        <span><i className="low" />0–4</span>
        <span><i className="medium" />5–14</span>
        <span><i className="high" />15+</span>
        <small>confirmações</small>
      </div>
      <p>A intensidade representa participação comunitária, {compact ? "não nível de perigo." : "NÃO nível de perigo. Proximidade de avisos não é classificação de risco."}</p>
    </aside>
  );
}
