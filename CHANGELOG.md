# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-10-25

### Added
- GoatCounter analytics (`exegesis.goatcounter.com`) on every page.
- Click events for the header's outbound links (discord, VR avatars, website source) and the NSFW gate's Continue/Skip buttons.
- Automatic click tracking for outbound links in entry and codex prose, via a rehype plugin (`src/lib/rehypeGoatcounterLinks.js`).
- "Read to end" events when a reader reaches the bottom nav of an entry or codex page after at least 10 seconds on the page.
- Analytics note on the about page.

## [1.0.0] - 2026-05-06

### Added
- Link to website source code in the header navigation pointing to `https://github.com/choccccy/exegesis-site`.
