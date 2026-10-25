/**
 * Tests for the GoatCounter outbound link rehype plugin.
 * Run with: node src/lib/rehypeGoatcounterLinks.test.js
 */

import assert from "assert";
import rehypeGoatcounterLinks from "./rehypeGoatcounterLinks.js";

const link = (href, text = "link", properties = {}) => ({
  type: "element",
  tagName: "a",
  properties: { href, ...properties },
  children: [{ type: "text", value: text }],
});

function run(links, frontmatterTitle = "Orbital Insertion") {
  const tree = {
    type: "root",
    children: [{ type: "element", tagName: "p", properties: {}, children: links }],
  };
  const file = { data: { astro: { frontmatter: { title: frontmatterTitle } } } };
  rehypeGoatcounterLinks()(tree, file);
  return links.map((l) => l.properties);
}

// External link gets tagged with name and page-aware title
{
  const [p] = run([link("https://en.wikipedia.org/wiki/Dyson_sphere", "Dyson sphere")]);
  assert.strictEqual(p.dataGoatcounterClick, "out/en.wikipedia.org/wiki/Dyson_sphere");
  assert.strictEqual(p.dataGoatcounterTitle, "Dyson sphere (from Orbital Insertion)");
}

// Internal, hash, mailto and own-site links are left alone
{
  const props = run([
    link("/entry/black-tangent/"),
    link("#section"),
    link("mailto:someone@example.com"),
    link("https://exegesis.space/codex/"),
    link("https://www.exegesis.space/codex/"),
  ]);
  for (const p of props) assert.strictEqual(p.dataGoatcounterClick, undefined, p.href);
}

// Query string dropped, hash kept, www stripped
{
  const [p] = run([link("https://www.example.com/a/b?utm_source=x#part")]);
  assert.strictEqual(p.dataGoatcounterClick, "out/example.com/a/b#part");
}

// Existing attributes are not overwritten
{
  const [a, b] = run([
    link("https://example.com/", "x", { dataGoatcounterClick: "custom" }),
    link("https://example.com/", "x", { dataGoatcounterTitle: "My title" }),
  ]);
  assert.strictEqual(a.dataGoatcounterClick, "custom");
  assert.strictEqual(a.dataGoatcounterTitle, undefined);
  assert.strictEqual(b.dataGoatcounterClick, "out/example.com/");
  assert.strictEqual(b.dataGoatcounterTitle, "My title");
}

// No frontmatter title: falls back to link text
{
  const [p] = run([link("https://example.com/", "Example")], null);
  assert.strictEqual(p.dataGoatcounterTitle, "Example");
}

console.log("rehypeGoatcounterLinks: all tests passed");
