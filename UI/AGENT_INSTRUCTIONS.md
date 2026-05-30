# Agent Instructions — Read This First

You are an LLM (Claude, GPT, Gemini, Cursor, Copilot, etc.) being asked to build or modify a project that must visually match **SchulterPlan**. This folder is the source of truth. Follow these rules.

---

## 1. The contract

Whatever framework you are working in (React / Vue / Svelte / Next / Astro / Nuxt / SwiftUI / native HTML / Flutter web), the design contract is:

> **The CSS in `UI/css/schulterplan.css` is canonical.** Tokens in `UI/tokens/tokens.css` are canonical. Anything else you produce must visually match a screenshot of `UI/examples/kitchen-sink.html` opened in a browser.

If you cannot use the CSS file directly (e.g. native mobile), translate **`UI/tokens/tokens.json`** into your platform's design-token format. Do not invent values.

---

## 2. Mandatory reading order

Before generating a single line of UI code, read in this order:

1. `README.md` — what this folder is.
2. `BRAND.md` — what SchulterPlan feels like (so you don't break the personality).
3. `DESIGN_SYSTEM.md` — colors, type, spacing, radii, shadows, motion.
4. `COMPONENTS.md` — anatomy of every component, class names, states.
5. `PATTERNS.md` — how components compose into screens.
6. `ACCESSIBILITY.md` — contrast & focus rules. Do not skip.

If the user gave you a specific task, you may then jump straight to the relevant `components/*.html` snippet.

---

## 3. Hard rules — do not violate

| # | Rule | Why |
|---|---|---|
| 1 | **Never invent a color.** Pull from `--primary`, `--accent`, `--danger`, `--success`, etc. | Brand consistency. |
| 2 | **Never use a font other than Inter.** | Identity. |
| 3 | **Always use the radius scale** (`--radius-sm/md/lg/xl` = 8/12/16/24). | Visual rhythm. |
| 4 | **Always use `font-variant-numeric: tabular-nums` on metric values.** | Numbers must not jitter when they change. |
| 5 | **Never produce a light theme** unless the user explicitly asks. SchulterPlan is dark-first. | Surgical context. |
| 6 | **Section labels are uppercase, 11px, weight 600, letter-spacing 1.2px, color `--text-muted`.** | Signature look. |
| 7 | **Primary buttons get a teal glow on hover** (`box-shadow: 0 0 20px var(--primary-glow)`). | Signature interaction. |
| 8 | **Accent (gold) buttons indicate a toggleable state** — solid gold when `active`, soft gold tint otherwise. | Consistent meaning. |
| 9 | **All translucent surfaces get `backdrop-filter: blur(16px)`** with the `-webkit-` prefix. | Required for Safari. |
| 10 | **Use `cubic-bezier(0.4, 0, 0.2, 1)` for transitions — never `ease` or `ease-in-out`.** | Motion personality. |

---

## 4. Decision tree for common requests

### "Build a new screen"
1. Pick a template from `UI/templates/`.
2. Compose with components from `UI/components/`.
3. Use existing tokens. Do not introduce new spacing/color values.
4. Validate against `ACCESSIBILITY.md`.

### "Add a new component that isn't here"
1. Check `COMPONENTS.md` — confirm it really doesn't exist.
2. Extend using existing tokens (radii, colors, transitions).
3. Match the closest existing component's signature (e.g., a new chip → mirror `.btn-sm`).
4. Add a snippet to `UI/components/` and document it in `COMPONENTS.md` before you finish.

### "Port to React / Vue / Svelte"
- The CSS classes are the API. Wrap them, don't reinvent.
- Example: `<Button variant="primary">` → `<button className="btn btn-primary">`.

### "Port to a backend admin / dashboard"
- Use `templates/planner-3col-layout.html` as the shell.
- Replace the 3D viewer area with your data view (table, chart, etc.).
- Keep the topbar, sidebars, section-labels exactly as defined.

### "Port to native mobile"
- Read `tokens/tokens.json`.
- Map: `--primary` → your platform's tint, `--bg-base` → background, `--bg-surface` → card surface.
- Maintain ratios: 8/12/16/24 radii, 0.2s easing, blur for translucent surfaces.

---

## 5. What "done" looks like

Before declaring the work complete, run this checklist:

- [ ] No hardcoded hex values outside `tokens.css` (use vars).
- [ ] No font other than Inter is loaded.
- [ ] All primary/accent/ghost button variants render correctly.
- [ ] Section labels match the uppercase 11px / 1.2px-spacing recipe.
- [ ] All metric numbers use tabular-nums.
- [ ] Hover state on `.btn-primary` shows the teal glow.
- [ ] Active state on `.btn-accent` is solid gold with shadow.
- [ ] Cards have a subtle border at 8% white and `backdrop-filter` if translucent.
- [ ] Inputs show a teal focus ring (`box-shadow: 0 0 0 3px var(--primary-glow)`).
- [ ] Visual diff against `examples/kitchen-sink.html` shows no surprise drift.

---

## 6. When the user asks you to deviate

Sometimes the user genuinely wants something different. When that happens:

1. **Confirm explicitly:** "This will deviate from the SchulterPlan design system — is that intentional?"
2. **Isolate the deviation** in its own CSS file/scope so the rest of the project stays canonical.
3. **Do not** silently rewrite tokens.

---

## 7. Files you should never edit

The contents of this `UI/` folder are intended to be **read-only from a downstream project's perspective**. If you need to evolve the design system itself, do it in the original SchulterPlan repository and re-export this folder.
