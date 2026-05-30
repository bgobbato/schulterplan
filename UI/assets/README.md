# Assets

Drop project-specific assets here. The SchulterPlan deliverable expects:

- **`logo_implantcast.png`** — the Implantcast wordmark/logomark used in the topbar. PNG with transparency, ~64 × 64 px at 2× density. The source file is in the parent project's `data/logo_implantcast.png`.

If the asset is missing the topbar will still render — the `<img>` `alt=""` falls back gracefully.

For the "SchulterPlan" wordmark beside the logo, no image is needed — it is rendered as text with a CSS gradient (see `.topbar-logo h1` in `css/schulterplan.css`).

## Adding new assets

1. Use SVG when possible (icons, illustrations).
2. PNGs should be 2× density (retina-ready).
3. Never use stock photography.
4. Keep file sizes lean — < 200 KB for any single asset shown in chrome.
