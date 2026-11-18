export type Point = readonly [x: number, y: number];
export type MapLayer = "roads" | "outline" | "a" | "b" | "c";
type MapLabel = "district" | "neighborhood" | "ellis" | "santanna" | "itapecerica" | "origin" | "destination" | "originLabel" | "destinationLabel" | "a" | "b" | "c";

export type MapArt = {
  size: Point;
  layers: Partial<Record<MapLayer, Point>>;
  labels: Partial<Record<MapLabel, Point>>;
  pins: Partial<Record<"theft" | "dark" | "other" | "cluster", Point>>;
};

// Coordenadas dos elementos cartográficos nos frames do Figma.
export const mapArt = {
  "home-mobile": {
    size: [430, 724],
    layers: { roads: [41.19, 125.11] },
    labels: {
      district: [34, 209.16], neighborhood: [327, 498.76], ellis: [51.13, 317.03], santanna: [280.39, 639.06], itapecerica: [215.49, 478.01],
    },
    pins: { theft: [128, 455.38], cluster: [260, 310] },
  },
  "plan-mobile": {
    size: [430, 360],
    layers: { roads: [41.19, 62.21], outline: [71.98, 92.02], a: [74.5, 94.5] },
    labels: {
      district: [34, 104], neighborhood: [327, 248], ellis: [51.13, 155.25], santanna: [280.39, 311.46], itapecerica: [215.49, 227.25],
      origin: [70, 259], destination: [308, 85], originLabel: [39, 297], destinationLabel: [249, 59],
    },
    pins: { theft: [128, 239], dark: [199, 178], other: [274, 131] },
  },
  "plan-desktop": {
    size: [1010, 970],
    layers: { roads: [96.45, 167.91], outline: [176.95, 255.98], a: [179.48, 258.5] },
    labels: {
      district: [81, 279], neighborhood: [768, 667], ellis: [89.74, 423.88], santanna: [600.07, 856.49], itapecerica: [467.23, 637.98],
      origin: [175, 708], destination: [740, 249], originLabel: [91, 800], destinationLabel: [586, 158],
    },
    pins: { theft: [302, 662], dark: [469, 498], other: [645, 371] },
  },
  "compare-mobile": {
    size: [430, 400],
    layers: { roads: [41.19, 69.04], outline: [71.98, 103], a: [74.52, 105.48], b: [74.52, 100.48], c: [74.52, 105.48] },
    labels: {
      district: [34, 115], neighborhood: [327, 275], ellis: [51.13, 173.25], santanna: [280.39, 347.46], itapecerica: [215.49, 254.25],
      origin: [70, 288], destination: [308, 96], originLabel: [39, 330], destinationLabel: [249, 65], a: [163, 130], b: [86, 160], c: [310, 255],
    },
    pins: { theft: [152, 247], dark: [199, 199], other: [274, 147] },
  },
  "compare-desktop": {
    size: [1010, 1040],
    layers: { roads: [96.45, 179.61], outline: [176.95, 274.98], a: [179.48, 277.47], b: [179.48, 264.47], c: [179.48, 277.47] },
    labels: {
      district: [81, 299], neighborhood: [768, 715], ellis: [89.74, 455.88], santanna: [600.07, 919.49], itapecerica: [467.23, 685.98],
      origin: [175, 760], destination: [740, 268], originLabel: [91, 858], destinationLabel: [586, 169], a: [540, 319], b: [263, 351], c: [515, 793],
    },
    pins: { theft: [302, 711], dark: [469, 535], other: [645, 399] },
  },
  "detail-mobile": {
    size: [430, 340],
    layers: { roads: [41.24, 59.23], outline: [71.98, 85.99], a: [74.52, 88.5] },
    labels: {
      district: [34, 98], neighborhood: [327, 234], ellis: [51.13, 146.25], santanna: [280.39, 293.46], itapecerica: [215.49, 213.25],
      origin: [70, 244], destination: [308, 79], originLabel: [39, 281], destinationLabel: [249, 55],
    },
    pins: { theft: [128, 225], dark: [199, 168], other: [274, 123] },
  },
  "detail-desktop": {
    size: [960, 1280],
    layers: { roads: [91.97, 221.18], outline: [168, 338.94], a: [170.5, 341.5] },
    labels: {
      district: [77, 368], neighborhood: [730, 880], ellis: [86.74, 561.88], santanna: [574.07, 1135.49], itapecerica: [447.23, 850.98],
      origin: [166, 937], destination: [703, 332], originLabel: [86, 1056], destinationLabel: [557, 208],
    },
    pins: { theft: [287, 877], dark: [445, 661], other: [613, 493] },
  },
  "pin-mobile": {
    size: [430, 370],
    layers: { roads: [41.15, 64.08], outline: [71.98, 94.02], a: [74.52, 96.5] },
    labels: {
      district: [34, 106], neighborhood: [327, 254], ellis: [51.13, 159.25], santanna: [280.39, 320.46], itapecerica: [215.49, 233.25],
      origin: [70, 266], destination: [308, 87], originLabel: [39, 305], destinationLabel: [249, 60],
    },
    pins: { theft: [128, 246], dark: [199, 183], other: [274, 135] },
  },
  "report-mobile": {
    size: [430, 290],
    layers: { roads: [41.15, 50.23], outline: [71.98, 72.99], a: [74.52, 75.49] },
    labels: {
      district: [34, 83], neighborhood: [327, 199], ellis: [51.13, 124.25], santanna: [280.39, 248.46], itapecerica: [215.49, 178.25],
      origin: [70, 207], destination: [308, 66], originLabel: [39, 239], destinationLabel: [249, 47],
    },
    pins: { theft: [128, 190], dark: [199, 141], other: [274, 103] },
  },
} satisfies Record<string, MapArt>;

export type MapArtId = keyof typeof mapArt;

// Tamanhos originais dos SVGs exportados do Figma.
export const artSizes: Record<string, Point> = {
  "compare-desktop-a": [575.001, 492.001],
  "compare-desktop-axes": [814.375, 834.345],
  "compare-desktop-b": [575.001, 505.032],
  "compare-desktop-c": [661.514, 609.448],
  "compare-desktop-grid": [1010, 1040],
  "compare-desktop-land": [1010, 1040],
  "compare-desktop-outline": [580.002, 497.001],
  "compare-desktop-roads": [814.375, 834.345],
  "compare-mobile-a": [248.001, 192.001],
  "compare-mobile-axes": [346.84, 320.965],
  "compare-mobile-b": [248.001, 197.026],
  "compare-mobile-c": [285.63, 237.363],
  "compare-mobile-grid": [430, 400],
  "compare-mobile-land": [430, 400],
  "compare-mobile-outline": [253.001, 197.001],
  "compare-mobile-roads": [346.84, 320.965],
  "detail-desktop-a": [547.001, 605.001],
  "detail-desktop-axes": [773.56, 1026.85],
  "detail-desktop-grid": [960, 1280],
  "detail-desktop-land": [960, 1280],
  "detail-desktop-outline": [552.002, 610.002],
  "detail-desktop-roads": [773.56, 1026.85],
  "detail-mobile-a": [248.001, 165.001],
  "detail-mobile-axes": [344.692, 272.762],
  "detail-mobile-grid": [430, 340],
  "detail-mobile-land": [430, 340],
  "detail-mobile-outline": [253.001, 170.001],
  "detail-mobile-roads": [344.692, 272.762],
  "home-mobile-axes": [347.176, 580.801],
  "home-mobile-grid": [430, 724],
  "home-mobile-land": [430, 724],
  "home-mobile-roads": [347.176, 580.801],
  "pin-mobile-a": [248.001, 179.001],
  "pin-mobile-axes": [346.18, 296.899],
  "pin-mobile-grid": [430, 370],
  "pin-mobile-land": [430, 370],
  "pin-mobile-outline": [253.001, 184.001],
  "pin-mobile-roads": [346.18, 296.899],
  "plan-desktop-a": [575.001, 459.001],
  "plan-desktop-axes": [813.547, 778.082],
  "plan-desktop-grid": [1010, 970],
  "plan-desktop-land": [1010, 970],
  "plan-desktop-outline": [580.001, 464.001],
  "plan-desktop-roads": [813.547, 778.082],
  "plan-mobile-a": [248.001, 174.001],
  "plan-mobile-axes": [347.176, 288.796],
  "plan-mobile-grid": [430, 360],
  "plan-mobile-land": [430, 360],
  "plan-mobile-outline": [253.001, 179.001],
  "plan-mobile-roads": [347.176, 288.796],
  "report-mobile-a": [248.001, 141.001],
  "report-mobile-axes": [346.691, 232.758],
  "report-mobile-grid": [430, 290],
  "report-mobile-land": [430, 290],
  "report-mobile-outline": [253.001, 146.001],
  "report-mobile-roads": [346.691, 232.758],
};
