/**
 * Characterization tests for star generation
 * These document EXACTLY how stars are currently being generated
 * so we can change the color distribution without accidentally
 * breaking spike behavior
 */

import assert from "assert";
import {
  generateStar,
  generateStarfield,
  analyzeStarfield,
  SPECTRAL_TYPES,
  WEIGHTS,
  SPIKE_ALPHA_MULTIPLIER,
  SPIKE_LENGTH_MULTIPLIER,
  BASE_SIZE,
} from "./starGenerator.js";

const TOTAL_WEIGHT = WEIGHTS.reduce((a, b) => a + b, 0);

// Deterministic seeded random for reproducible tests
function seededRandom(seed) {
  let s = seed;
  return function () {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

// --- Constants ---

assert.strictEqual(SPIKE_ALPHA_MULTIPLIER, 0.48, "spike alpha multiplier should be 0.48");
assert.strictEqual(SPIKE_LENGTH_MULTIPLIER, 32, "spike length multiplier should be 32");
assert.strictEqual(BASE_SIZE, 1, "base size should be 1");

// --- Spectral types ---

console.log(`\n=== Spectral Type Definitions (${SPECTRAL_TYPES.length} types) ===`);
SPECTRAL_TYPES.forEach((st, i) => {
  console.log(`  [${i}] ${st.label}: color=${st.color}, brightness=${st.brightness}`);
});

// --- Weight distribution ---

console.log(`\n=== Weight Distribution (total=${TOTAL_WEIGHT}) ===`);
const labels = ["O/B", "O/B", "O/B", "A", "A", "A", "A", "A", "F", "F", "F", "F", "G", "G", "G", "K", "K", "K", "M", "M", "M"];
WEIGHTS.forEach((w, i) => {
  const pct = ((w / TOTAL_WEIGHT) * 100).toFixed(2);
  console.log(`  [${i}] ${labels[i]}: weight=${w} (${pct}%)`);
});

// --- Generate 10,000 stars to characterize the distribution ---

const SEED = 42;
const rand = seededRandom(SEED);
const stars = generateStarfield(10000, 1920, 1080, rand);
const stats = analyzeStarfield(stars);

console.log(`\n=== Starfield Analysis (${stats.total} stars) ===`);

// Brightness distribution
console.log("\nBrightness distribution:");
Object.entries(stats.brightnessDistribution).forEach(([bucket, count]) => {
  const pct = ((count / stats.total) * 100).toFixed(1);
  const bar = "█".repeat(Math.floor(count / 50));
  console.log(`  ${bucket}: ${count} (${pct}%) ${bar}`);
});

// Spectral type distribution
console.log("\nSpectral type distribution:");
Object.entries(stats.spectralDistribution).forEach(([type, count]) => {
  const pct = ((count / stats.total) * 100).toFixed(1);
  console.log(`  ${type}: ${count} (${pct}%)`);
});

// Spike alpha stats
console.log("\nSpike alpha statistics:");
console.log(`  Min: ${stats.spikeAlphaStats.min.toFixed(4)}`);
console.log(`  Max: ${stats.spikeAlphaStats.max.toFixed(4)}`);
console.log(`  Mean: ${stats.spikeAlphaStats.mean.toFixed(4)}`);
console.log(`  Median: ${stats.spikeAlphaStats.median.toFixed(4)}`);
console.log(`  P90: ${stats.spikeAlphaStats.p90.toFixed(4)}`);
console.log(`  P95: ${stats.spikeAlphaStats.p95.toFixed(4)}`);
console.log(`  P99: ${stats.spikeAlphaStats.p99.toFixed(4)}`);

// Visible spike counts
console.log("\nStars with visible spikes (alpha > threshold):");
Object.entries(stats.visibleSpikeCounts).forEach(([thresh, count]) => {
  const pct = ((count / stats.total) * 100).toFixed(1);
  console.log(`  ${thresh}: ${count} (${pct}%)`);
});

// Prominent spike stars (alpha > 0.3)
console.log(`\nProminent spike stars (alpha > 0.3): ${stats.prominentSpikeStarsCount} (${((stats.prominentSpikeStarsCount / stats.total) * 100).toFixed(1)}%)`);

// Show the top 10 most prominent spike stars
if (stats.prominentSpikeStarDetails.length > 0) {
  const top10 = stats.prominentSpikeStarDetails
    .sort((a, b) => b.spikeAlpha - a.spikeAlpha)
    .slice(0, 10);
  console.log("\nTop 10 most prominent:");
  top10.forEach(s => {
    console.log(`  ${s.label} ${s.color} brightness=${s.brightness} spikeAlpha=${s.spikeAlpha.toFixed(3)} spikeLength=${s.spikeLength}`);
  });
}

// --- Assertions for future change detection ---

// 1. Bright stars (opacity >= 0.8) should be rare
const brightStars = stars.filter(s => s.baseOpacity >= 0.8);
const brightPct = (brightStars.length / stars.length) * 100;
console.log(`\n=== Change Detection Assertions ===`);
console.log(`Bright stars (opacity >= 0.8): ${brightStars.length} (${brightPct.toFixed(1)}%)`);
assert(brightPct < 5, `Expected <5% bright stars, got ${brightPct.toFixed(1)}%`);

// 2. Dim stars (opacity < 0.3) should dominate
const dimStars = stars.filter(s => s.baseOpacity < 0.3);
const dimPct = (dimStars.length / stars.length) * 100;
console.log(`Dim stars (opacity < 0.3): ${dimStars.length} (${dimPct.toFixed(1)}%)`);
assert(dimPct > 60, `Expected >60% dim stars, got ${dimPct.toFixed(1)}%`);

// 3. Warm stars (K/M types) should be rare
const warmStars = stars.filter(s => s.label === "K" || s.label === "M");
const warmPct = (warmStars.length / stars.length) * 100;
console.log(`Warm stars (K/M): ${warmStars.length} (${warmPct.toFixed(1)}%)`);
assert(warmPct < 10, `Expected <10% warm stars, got ${warmPct.toFixed(1)}%`);

// 4. Yellow stars (G type) should be visible but not dominant
const yellowStars = stars.filter(s => s.label === "G");
const yellowPct = (yellowStars.length / stars.length) * 100;
console.log(`Yellow stars (G): ${yellowStars.length} (${yellowPct.toFixed(1)}%)`);
assert(yellowPct > 1, `Expected >1% yellow stars, got ${yellowPct.toFixed(1)}%`);

// 3. Spike length should be consistent
stars.forEach(s => {
  assert.strictEqual(s.spikeLength, BASE_SIZE * SPIKE_LENGTH_MULTIPLIER, "all stars should have same spike length");
});
console.log(`All stars have consistent spike length: ${BASE_SIZE * SPIKE_LENGTH_MULTIPLIER}`);

// 4. Spike alpha should scale linearly with brightness
stars.forEach(s => {
  assert.strictEqual(s.spikeAlpha, s.baseOpacity * SPIKE_ALPHA_MULTIPLIER, "spike alpha should scale linearly with brightness");
});
console.log("All stars have correct spike alpha = baseOpacity * 0.48");

// 5. All spectral types should have correct RGB parsing
stars.forEach(s => {
  const hex = s.color;
  const expectedR = parseInt(hex.slice(1, 3), 16);
  const expectedG = parseInt(hex.slice(3, 5), 16);
  const expectedB = parseInt(hex.slice(5, 7), 16);
  assert.strictEqual(s.r, expectedR, "red component mismatch");
  assert.strictEqual(s.g, expectedG, "green component mismatch");
  assert.strictEqual(s.b, expectedB, "blue component mismatch");
});
console.log("All stars have correct RGB parsing");

console.log("\n✅ All characterization assertions passed");
