// Validates entry prev/next chain integrity at build time.
// Run with: node scripts/validate-chains.mjs

import { readFileSync, readdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const entriesDir = join(__dirname, '..', 'src', 'content', 'entry');

function parseFrontmatter(file) {
  const content = readFileSync(file, 'utf-8');
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;

  const frontmatter = {};
  match[1].split('\n').forEach(line => {
    const m = line.match(/^(\w+):\s*(.+)$/);
    if (m) {
      let value = m[2].trim();
      // Parse quoted strings
      if (value.startsWith("'") && value.endsWith("'")) {
        value = value.slice(1, -1);
      } else if (value === 'true') {
        value = true;
      } else if (value === 'false') {
        value = false;
      } else if (value === 'null') {
        value = null;
      } else if (!isNaN(value)) {
        value = Number(value);
      }
      frontmatter[m[1]] = value;
    }
  });
  return frontmatter;
}

const entries = [];
const files = readdirSync(entriesDir).filter(f => f.endsWith('.mdx'));

for (const file of files) {
  const fm = parseFrontmatter(join(entriesDir, file));
  if (fm && fm.title) {
    entries.push(fm);
  }
}

const byTitle = new Map(entries.map(e => [e.title, e]));
const errors = [];
const warnings = [];

for (const entry of entries) {
  const { title, previousEntry, nextEntry, status } = entry;

  if (previousEntry) {
    const prev = byTitle.get(previousEntry);
    if (!prev) {
      errors.push(`"${title}" → previousEntry "${previousEntry}" not found`);
    } else if (prev.nextEntry !== title) {
      warnings.push(
        `"${title}" → previousEntry "${previousEntry}" but "${previousEntry}" → nextEntry is "${prev.nextEntry}"`
      );
    }
  }

  if (nextEntry) {
    const next = byTitle.get(nextEntry);
    if (!next) {
      errors.push(`"${title}" → nextEntry "${nextEntry}" not found`);
    } else if (next.previousEntry !== title) {
      warnings.push(
        `"${title}" → nextEntry "${nextEntry}" but "${nextEntry}" → previousEntry is "${next.previousEntry}"`
      );
    }
  }
}

if (errors.length > 0) {
  console.error('❌ Chain validation errors:');
  errors.forEach(e => console.error(`  - ${e}`));
}
if (warnings.length > 0) {
  console.warn('⚠️  Chain validation warnings:');
  warnings.forEach(w => console.warn(`  - ${w}`));
}
if (errors.length === 0 && warnings.length === 0) {
  console.log('✅ All entry chains valid');
}
if (errors.length > 0) {
  process.exit(1);
}
