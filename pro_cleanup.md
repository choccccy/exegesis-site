# Exegesis Site — Professional Web Dev Audit

## THE GOOD ✅

### 1. Solid Astro Foundation
- Astro 5.x with proper static output — good choice for a content site
- Strict TypeScript config with `strictNullChecks`
- Proper use of content collections with Zod schema validation
- Clean `getStaticPaths` implementation for dynamic routes

### 2. Thoughtful Architecture
- Good component separation: `BaseHead`, `Header`, `NavButton`, `DialogueBox`, `EntryNavigation`, `WarningBanner`
- Layout abstraction with `PageLayout`, `Entry`, and `Codex` is the right pattern
- RSS feed + sitemap integration — proper SEO hygiene
- Open Graph + Twitter Card meta done right in `BaseHead.astro`

### 3. Accessibility Done Right
- `aria-label`, `role="navigation"`, `.sr-only` class with proper `clip-path` technique
- Semantic HTML structure, proper `<nav>` usage
- Screen-reader-friendly navigation labels

### 4. Creative UI Components
- `DialogueBox.astro` — character-colored dialogue blocks with block/inline detection
- `NavButton` with `clip-path` arrow shapes
- `WarningBanner` with hazard-stripe gradient — thematic and well-executed
- NSFW gating with `localStorage` persistence

### 5. Responsive Design
- Consistent 840px breakpoint across components
- Header has a smart `ResizeObserver`-based stacking detector with `requestAnimationFrame` debounce
- Entry navigation collapses from grid to flex column properly

### 6. Performance-Conscious
- Font preloading with `crossorigin` attributes
- `font-display: swap` on all `@font-face` declarations
- SVG asset optimization (logos stay as SVGs)
- Static build = no server overhead

### 7. Content Strategy
- Entry numbering with gap-filling "in-progress" placeholders
- `_entry_todo.md` tracks content pipeline
- Clear published/unpublished workflow

---

## THE BAD ⚠️

### 1. Codex System is Broken (High Priority)
- `/codex/index.astro` queries `getCollection('codex')` but the collection is commented out in `content.config.ts`
- `/codex/[...slug].astro` is a **broken copy-paste** — queries `'entry'` collection instead of `'codex'`, uses `Entry` layout, types as `CollectionEntry<'entry'>`
- 15+ codex MDX files exist in `src/content/codex/` but are completely inaccessible
- Build outputs warning: `The collection "codex" does not exist or is empty`

### 2. About Page is Broken
- Uses `Lorem Ipsum` placeholder text
- `heroImage` references `AboutHeroImage` — invalid import path (should be `../assets/...`)
- Passes `pubDate` to `Entry` layout, but `pubDate` isn't in the entry schema

### 3. Duplicate/Dead Code
- `AuthorBanner.astro` is an **exact byte-for-byte duplicate** of `EntryNavigation.astro` — confirmed via `diff`. Not imported anywhere.
- `Footer.astro` is imported but **commented out in all three layouts** — social links are non-functional
- Header has commented-out links to codex and about pages

### 4. Entry.astro and Codex.astro are ~95% Identical
- Only difference: `.title` padding (`1em 1em` vs `1em 0`)
- Should be consolidated into a single layout with a prop

### 5. NSFW Gate Bug
- `Entry.astro` has **duplicate `type` props** on the confirm button:
  ```astro
  <NavButton
    id="nsfw-confirm-btn"
    type="default"
    type="warning"  <!-- This overrides the first -->
  ```
- The second `type="warning"` always wins — probably unintended

### 6. Image Handling Issues
- `BaseHead.astro` uses `new URL(image.src, Astro.url)` for OG images — can produce invalid URLs for assets processed by Astro's image pipeline
- Hero images in entry listing page use `entry.data.heroImage.src` directly — bypasses Astro's image optimization

### 7. CSS Specificity Wars
- `DialogueBox.astro` uses `!important` on `.db:not(p .db)` and `p .db` rules — fragile and hard to override
- `is:global` on DialogueBox styles means they leak into the global scope — intentional but risky

### 8. Brittle Entry Chaining System
- Entry prev/next navigation relies on **manual `previousEntry` and `nextEntry` string fields** in frontmatter, matched against `title`
- These can silently get out of sync — e.g., `Babel Contingency` had `nextEntry: null` when it should've been `'Distributed Resolve'`, breaking the forward chain
- No validation exists to catch broken chains at build time
- **Recommendation:** Derive prev/next links automatically from `entryNumber` ordering, or add a Zod refinement that validates chain integrity at build time

---

## THE UGLY 💀

### 1. No Package Name
- `package.json` has `"name": ""` — will break any tooling that expects a valid name (monorepo setups, deploy platforms, etc.)

### 2. Massive Font Payload
- **18 font files** preloaded in `<head>` — that's ~18 render-blocking requests
- JetBrainsMono has 9 weights × 2 styles preloaded even though most pages probably only need Regular
- Atkinson only has Regular + Bold but JetBrainsMono has the full family tree
- **Recommendation:** Only preload the 2-3 most critical fonts, lazy-load the rest via `font-display: swap`

### 3. Inline Script in Entry.astro
- NSFW gating logic is inline `is:inline` script — can't be tree-shaken, minified, or cached separately
- No error handling if `#nsfw-confirm-btn` or `#nsfw-skip-btn` don't exist
- `localStorage` access isn't wrapped in try/catch — will throw in privacy-mode browsers

### 4. No Testing or CI Quality Gates
- GitHub workflow exists (deploy on push to main) but has **no linting, type-checking, or build verification** before deploy
- No `astro check` or TypeScript validation in CI
- No preview/deploy staging — every push to main goes live

### 5. Hardcoded External URLs
- Discord invite (`https://discord.gg/CAHWY2wKWu`) and GitHub VR avatars repo are hardcoded in `Header.astro`
- No environment variable abstraction — these can't be changed per-deployment

### 6. Missing Error Boundaries
- `404.astro` is minimal but there's no `500.astro` or error page
- No fallback for failed image loads in entries
- No loading states for navigation

### 7. Commented-Out Code Everywhere
- `Header.astro`: commented-out logo link wrapper, commented-out social links section
- `PageLayout.astro`: commented-out title header, commented-out Footer
- `global.css`: commented-out `.prose p` rules, commented-out image border styles
- `entry/index.astro`: commented-out first-child featured entry styling
- **This is dead weight** — either implement or delete, don't leave as archaeology

---

## Priority Recommendations

| Priority | Action | Affected Files |
|----------|--------|----------------|
| **P0** | Fix codex collection: uncomment in `content.config.ts`, fix `/codex/[...slug].astro` to query `'codex'` | `content.config.ts`, `pages/codex/[...slug].astro`, `pages/codex/index.astro` |
| **P0** | Fix or remove `/about` page | `pages/about.astro` |
| **P1** | Delete `AuthorBanner.astro` (duplicate) | `components/AuthorBanner.astro` |
| **P1** | Consolidate `Entry.astro` and `Codex.astro` into single layout | `layouts/Entry.astro`, `layouts/Codex.astro` |
| **P1** | Fix duplicate `type` prop on NSFW confirm button | `layouts/Entry.astro` |
| **P1** | Add package name to `package.json` | `package.json` |
| **P2** | Add `astro check` + `tsc --noEmit` to CI before deploy | `.github/workflows/*.yml` |
| **P2** | Automate entry chaining: derive prev/next from `entryNumber` or add build-time chain validation | `content.config.ts`, `components/EntryNavigation.astro` |
| **P2** | Reduce font preloads to 3-4 critical files | `components/BaseHead.astro` |
| **P2** | Wrap `localStorage` in try/catch for NSFW gate | `layouts/Entry.astro` |
| **P2** | Clean up all commented-out code or implement it | `Header.astro`, `PageLayout.astro`, `global.css`, `entry/index.astro` |
| **P3** | Add `500.astro` error page | `pages/500.astro` (new) |
| **P3** | Extract external URLs to environment variables | `Header.astro`, `consts.ts` |
| **P3** | Fix OG image URL generation for Astro-processed assets | `components/BaseHead.astro` |

---

## Summary

This is a well-architected Astro site with good component design and accessibility, but it has significant dead code, a broken codex system, and needs CI quality gates. The creative vision is clear and the technical foundation is solid — it just needs cleanup and the codex activation to be production-ready.
