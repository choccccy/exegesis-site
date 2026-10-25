/**
 * Rehype plugin: tag outbound links in Markdown/MDX prose for GoatCounter
 * click tracking. count.js picks up any element with data-goatcounter-click,
 * so adding the attributes at build time is all that's needed.
 *
 * [Dyson sphere](https://en.wikipedia.org/wiki/Dyson_sphere) becomes
 *   data-goatcounter-click="out/en.wikipedia.org/wiki/Dyson_sphere"
 *   data-goatcounter-title="Dyson sphere (from Orbital Insertion)"
 */

const SITE_HOST = 'exegesis.space';

function textContent(node) {
  if (node.type === 'text') return node.value;
  return (node.children || []).map(textContent).join('');
}

function walk(node, fn) {
  fn(node);
  for (const child of node.children || []) walk(child, fn);
}

export function outboundEventName(href) {
  let url;
  try {
    url = new URL(href);
  } catch {
    return null; // relative links, #hash, etc.
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return null;
  const host = url.hostname.replace(/^www\./, '');
  if (host === SITE_HOST) return null;
  // Query strings are dropped so tracking params don't split the counts
  return `out/${host}${url.pathname}${url.hash}`;
}

export default function rehypeGoatcounterLinks() {
  return (tree, file) => {
    const pageTitle = file?.data?.astro?.frontmatter?.title;

    walk(tree, (node) => {
      if (node.type !== 'element' || node.tagName !== 'a') return;
      const props = node.properties || (node.properties = {});
      if (props.dataGoatcounterClick) return;

      const name = outboundEventName(String(props.href ?? ''));
      if (!name) return;

      const text = textContent(node).trim() || name;
      props.dataGoatcounterClick = name;
      props.dataGoatcounterTitle ??= pageTitle ? `${text} (from ${pageTitle})` : text;
    });
  };
}
