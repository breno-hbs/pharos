"use client";

import { useState, type CSSProperties, type ReactNode } from "react";
import { categories, getStop, observations, participationBand, type Category, type Participation, type Trip } from "./data";
import { artSizes, mapArt, type MapArt, type MapArtId, type MapLayer, type Point } from "./map-art";
import { Icon } from "./ui";

type RouteLine = "a" | "b" | "c";
type MapMode = "home" | "plan" | "compare" | "detail" | "pin" | "report";

const mapVariants: Record<MapMode, readonly [MapArtId, MapArtId]> = {
  home: ["home-mobile", "plan-desktop"],
  plan: ["plan-mobile", "plan-desktop"],
  compare: ["compare-mobile", "compare-desktop"],
  detail: ["detail-mobile", "detail-desktop"],
  pin: ["pin-mobile", "detail-desktop"],
  report: ["report-mobile", "detail-desktop"],
};

function position([x, y]: Point, [width, height]: Point): CSSProperties {
  return { left: `${x / width * 100}%`, top: `${y / height * 100}%` };
}

function Layer({ frame, name, at, size, className = "" }: {
  frame: MapArtId;
  name: string;
  at: Point;
  size: Point;
  className?: string;
}) {
  const asset = `${frame}-${name}`;
  const [width, height] = artSizes[asset];
  return (
    <img
      className={`map-layer ${className}`}
      src={`/${asset}.svg`}
      alt=""
      style={{ ...position(at, size), width: `${width / size[0] * 100}%`, height: `${height / size[1] * 100}%` }}
    />
  );
}

function MapDrawing({ frame, mode, trip, selected, filters, participation, expanded, onExpand, onPin }: {
  frame: MapArtId;
  mode: MapMode;
  trip: Trip;
  selected: RouteLine;
  filters: Category[];
  participation: Participation;
  expanded: boolean;
  onExpand: () => void;
  onPin?: (category: Category) => void;
}) {
  const art: MapArt = mapArt[frame];
  const desktop = frame.endsWith("desktop");
  const isHome = mode === "home";
  const routeFrame = desktop ? "compare-desktop" : "compare-mobile";
  const comparisonArt = mapArt[routeFrame];
  const showAlternatives = mode === "compare";
  const drawLayer = (key: MapLayer, className?: string) => {
    const at = art.layers[key];
    return at && <Layer frame={frame} name={key} at={at} size={art.size} className={className} />;
  };
  const labelStyle = (key: keyof MapArt["labels"]) => position(art.labels[key]!, art.size);
  const placeLabels = [
    ["district", "CAPÃO REDONDO"],
    ["neighborhood", "VILA FUNDÃO"],
    ["ellis", "Av. Ellis Maas"],
    ["santanna", "Av. Comendador Sant’Anna"],
    ["itapecerica", "Estr. de Itapecerica"],
  ] as const;

  return (
    <>
      <Layer frame={frame} name="land" at={[0, 0]} size={art.size} />
      <Layer frame={frame} name="grid" at={[0, 0]} size={art.size} />
      {drawLayer("roads")}
      <Layer frame={frame} name="axes" at={art.layers.roads!} size={art.size} />
      {!isHome && (
        <>
          {showAlternatives && selected !== "a" && drawLayer("a", "route-inactive")}
          {(["b", "c"] as const).map((route) => {
            if (!showAlternatives && route !== selected) return null;
            const source = art.layers[route] ? frame : routeFrame;
            const geometry = art.layers[route] ? art : comparisonArt;
            return <Layer key={route} frame={source} name={route} at={geometry.layers[route]!} size={geometry.size} className={route === selected ? "route-highlight" : ""} />;
          })}
          {selected === "a" && drawLayer("outline")}
          {selected === "a" && drawLayer("a")}
        </>
      )}
      {placeLabels.map(([key, text]) => art.labels[key] && <span key={key} className={`map-label ${key}`} style={labelStyle(key)}>{text}</span>)}
      {!isHome && art.labels.origin && (
        <>
          <span className="map-origin" style={labelStyle("origin")}><Icon name="origin" /></span>
          <span className="map-destination" style={labelStyle("destination")}><Icon name="train" /></span>
          <span className="map-label place" style={labelStyle("originLabel")}>{getStop(trip.origin).short}</span>
          <span className="map-label place destination-label" style={labelStyle("destinationLabel")}>{getStop(trip.destination).short}</span>
        </>
      )}
      {showAlternatives && (["a", "b", "c"] as const).map((route, i) => (
        <span key={route} className={`map-label route-label route-${route} ${selected === route ? "current" : ""}`} style={labelStyle(route)}>
          {route.toUpperCase()} · {[32, 39, 44][i]} min
        </span>
      ))}
      {art.pins.cluster && filters.some((category) => category !== "theft") && !expanded && (
        <button type="button" className="map-cluster" style={position(art.pins.cluster, art.size)} onClick={onExpand} aria-label="Expandir agrupamento de relatos">
          {filters.filter((category) => category !== "theft").length}
        </button>
      )}
      {categories.map(({ id, label, icon }) => {
        if (!filters.includes(id)) return null;
        let coordinates = art.pins[id];
        if (!coordinates && expanded && id !== "theft") coordinates = id === "dark" ? [235, 330] : [288, 283];
        if (!coordinates) return null;
        const count = observations[id].count + Number(participation[id] === "confirmed");
        const marker = <><Icon name={icon} /><small>{count}</small></>;
        const props = { className: `map-pin ${participationBand(count)}`, style: position(coordinates, art.size) };
        return onPin
          ? <button key={id} type="button" {...props} aria-label={`${label}, ${count} confirmações`} onClick={() => onPin(id)}>{marker}</button>
          : <span key={id} {...props} aria-label={`${label}, ${count} confirmações`}>{marker}</span>;
      })}
    </>
  );
}

export function MapView({ mode, trip, selected = "a", participation = {}, onPin, children }: {
  mode: MapMode;
  trip: Trip;
  selected?: RouteLine;
  participation?: Participation;
  onPin?: (category: Category) => void;
  children?: ReactNode;
}) {
  const [hidden, setHidden] = useState<Category[]>([]);
  const [zoom, setZoom] = useState(1);
  const [expanded, setExpanded] = useState(false);
  const frames = mapVariants[mode];
  const filters = categories.map(({ id }) => id).filter((id) => !hidden.includes(id));
  return (
    <section className={`map map-${mode}`} aria-label="Mapa ilustrativo do Capão Redondo">
      {frames.map((frame, index) => (
        <div key={index} className={`map-art map-art-${index === 0 ? "mobile" : "desktop"}`} style={{ transform: `scale(${zoom})` }}>
          <MapDrawing frame={frame} mode={mode} trip={trip} selected={selected} filters={filters}
            participation={participation} expanded={expanded} onPin={onPin}
            onExpand={() => { setExpanded(true); setZoom((value) => Math.max(1.2, value)); }} />
        </div>
      ))}
      <div className="map-tools">
        {mode !== "report" && (
          <div className="map-filters" aria-label="Categorias visíveis no mapa">
            {categories.map(({ id, label, icon }) => (
              <button key={id} type="button" aria-pressed={!hidden.includes(id)} onClick={() => setHidden((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id])}>
                <Icon name={icon} />{label}
              </button>
            ))}
          </div>
        )}
        <p className="map-caption">{mode === "home" ? "Pins comunitários · agrupamentos contam relatos" : "Intensidade = participação, não nível de perigo"}</p>
      </div>
      <div className="map-controls">
        <div>
          <button type="button" aria-label="Ampliar mapa" disabled={zoom >= 1.8} onClick={() => setZoom((value) => Math.min(value + 0.2, 1.8))}><Icon name="plus" /></button>
          <button type="button" aria-label="Reduzir mapa" disabled={zoom <= 1} onClick={() => setZoom((value) => Math.max(value - 0.2, 1))}><Icon name="minus" /></button>
        </div>
        <button type="button" aria-label="Centralizar mapa" onClick={() => { setZoom(1); setExpanded(false); }}><Icon name="locate" /></button>
      </div>
      {mode !== "home" && <div className="map-footer"><span className="map-scale"><i />200 m*</span><span>*Mapa e escala ilustrativos · não operacional</span></div>}
      {children}
    </section>
  );
}
