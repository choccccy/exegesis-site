/**
 * Star generation logic extracted from StarfieldBackground
 * Used both by the component and by tests
 */

// Spectral class definitions: color + brightness
const SPECTRAL_TYPES = [
  // O/B - blue-white, very bright, extremely rare
  { color: "#d0d8ff", brightness: 0.95, label: "O/B" },
  { color: "#c8d0ff", brightness: 0.9, label: "O/B" },
  { color: "#e0e8ff", brightness: 0.85, label: "O/B" },
  // A - white, bright, rare
  { color: "#ffffff", brightness: 0.8, label: "A" },
  { color: "#f0f0ff", brightness: 0.75, label: "A" },
  { color: "#e8e8ff", brightness: 0.7, label: "A" },
  // F - yellow-white, moderate-bright
  { color: "#fff8f0", brightness: 0.65, label: "F" },
  { color: "#fff0e0", brightness: 0.6, label: "F" },
  { color: "#fffff0", brightness: 0.55, label: "F" },
  // G - yellow, moderate
  { color: "#ffe8b0", brightness: 0.5, label: "G" },
  { color: "#ffe0a0", brightness: 0.45, label: "G" },
  // K giants - orange, dim-moderate (rare)
  { color: "#ffb060", brightness: 0.35, label: "K" },
  { color: "#ffa040", brightness: 0.3, label: "K" },
  // M supergiants - red, dim (very rare)
  { color: "#ff6040", brightness: 0.2, label: "M" },
  { color: "#ff4020", brightness: 0.15, label: "M" },
  // Dim background stars: grey-white (distant A/F/G types)
  { color: "#ffffff", brightness: 0.25, label: "dim" },
  { color: "#f8f8ff", brightness: 0.2, label: "dim" },
  { color: "#f0f0f8", brightness: 0.15, label: "dim" },
  { color: "#e8e8f0", brightness: 0.1, label: "dim" },
  { color: "#e0e0e8", brightness: 0.08, label: "dim" },
  { color: "#d8d8e0", brightness: 0.05, label: "dim" },
];

// Weight distribution
const WEIGHTS = [
  1, 0, 0,            // O/B: blue-white (only the brightest)
  1, 0, 0,            // A: white (only the 0.8 variant)
  1, 1, 1,            // F: yellow-white
  2, 2,               // G: yellow
  3, 3,               // K: orange (rare giants)
  1, 1,               // M: red (very rare supergiants)
  25, 25, 25, 25, 25, 25, // Dim white/grey background
];

const TOTAL_WEIGHT = WEIGHTS.reduce((a, b) => a + b, 0);

const SPIKE_ALPHA_MULTIPLIER = 0.48;
const BASE_SIZE = 1;
const SPIKE_LENGTH_MULTIPLIER = 32; // spikeLength = baseSize * 32

function generateStar(width, height, randFn = Math.random) {
  const x = randFn() * width;
  const y = randFn() * height;

  // Weighted random selection of spectral type
  let rand = randFn() * TOTAL_WEIGHT;
  let typeIdx = 0;
  for (let i = 0; i < WEIGHTS.length; i++) {
    rand -= WEIGHTS[i];
    if (rand <= 0) { typeIdx = i; break; }
  }

  const spectralType = SPECTRAL_TYPES[typeIdx];
  const color = spectralType.color;
  const baseOpacity = spectralType.brightness;
  const label = spectralType.label;

  // Parse RGB
  const r = parseInt(color.slice(1, 3), 16);
  const g = parseInt(color.slice(3, 5), 16);
  const b = parseInt(color.slice(5, 7), 16);

  // Spike properties
  const spikeAlpha = baseOpacity * SPIKE_ALPHA_MULTIPLIER;
  const spikeLength = BASE_SIZE * SPIKE_LENGTH_MULTIPLIER;

  return {
    x, y,
    color,
    label,           // spectral type label
    r, g, b,
    baseOpacity,
    spikeAlpha,
    spikeLength,
  };
}

function generateStarfield(count, width, height, randFn = Math.random) {
  const stars = [];
  for (let i = 0; i < count; i++) {
    stars.push(generateStar(width, height, randFn));
  }
  return stars;
}

function analyzeStarfield(stars) {
  const total = stars.length;

  // Brightness distribution
  const brightnessBuckets = {
    "0.0-0.1": 0, "0.1-0.2": 0, "0.2-0.3": 0, "0.3-0.4": 0,
    "0.4-0.5": 0, "0.5-0.6": 0, "0.6-0.7": 0, "0.7-0.8": 0,
    "0.8-0.9": 0, "0.9-1.0": 0,
  };
  stars.forEach(s => {
    const bucket = Math.min(Math.floor(s.baseOpacity * 10), 9);
    const key = `${bucket * 0.1}-${(bucket + 1) * 0.1}`;
    brightnessBuckets[key]++;
  });

  // Spectral type distribution
  const spectralDist = {};
  stars.forEach(s => {
    spectralDist[s.label] = (spectralDist[s.label] || 0) + 1;
  });

  // Spike alpha statistics
  const spikeAlphas = stars.map(s => s.spikeAlpha);
  const sorted = [...spikeAlphas].sort((a, b) => a - b);
  const spikeAlphaStats = {
    min: sorted[0],
    max: sorted[sorted.length - 1],
    median: sorted[Math.floor(sorted.length / 2)],
    mean: spikeAlphas.reduce((a, b) => a + b, 0) / total,
    p90: sorted[Math.floor(sorted.length * 0.9)],
    p95: sorted[Math.floor(sorted.length * 0.95)],
    p99: sorted[Math.floor(sorted.length * 0.99)],
  };

  // Count stars with "visible" spikes (alpha > threshold)
  const visibleThresholds = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4];
  const visibleSpikeCounts = {};
  visibleThresholds.forEach(t => {
    visibleSpikeCounts[`>${t}`] = stars.filter(s => s.spikeAlpha > t).length;
  });

  // Color distribution
  const colorDist = {};
  stars.forEach(s => {
    colorDist[s.color] = (colorDist[s.color] || 0) + 1;
  });

  // Stars with prominent spikes (alpha > 0.3, which is ~brightness > 0.625)
  const prominentSpikeStars = stars.filter(s => s.spikeAlpha > 0.3);

  return {
    total,
    brightnessDistribution: brightnessBuckets,
    spectralDistribution: spectralDist,
    spikeAlphaStats,
    visibleSpikeCounts,
    colorDistribution: colorDist,
    prominentSpikeStarsCount: prominentSpikeStars.length,
    prominentSpikeStarDetails: prominentSpikeStars.map(s => ({
      color: s.color,
      label: s.label,
      brightness: s.baseOpacity,
      spikeAlpha: s.spikeAlpha,
      spikeLength: s.spikeLength,
    })),
  };
}

export { generateStar, generateStarfield, analyzeStarfield, SPECTRAL_TYPES, WEIGHTS, SPIKE_ALPHA_MULTIPLIER, SPIKE_LENGTH_MULTIPLIER, BASE_SIZE };
