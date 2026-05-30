# Components

Every component the SchulterPlan UI ships with. Each entry lists the class API, states, an HTML snippet path, and do/don't notes.

> Reference snippets live in `UI/components/*.html`. Copy-paste them; do not refactor the class names.

---

## Button — `.btn`

The atom. All buttons share spacing, transitions, and the `:active` micro-scale.

| Variant | Class | Use |
|---|---|---|
| Primary | `.btn .btn-primary` | The single most important action on a screen. |
| Flat (tinted) | `.btn .btn-flat` | Secondary brand action. Soft teal background. |
| Ghost (outlined) | `.btn .btn-ghost` | Tertiary actions, toolbar buttons. |
| Accent (toggleable) | `.btn .btn-accent` | Adds `.active` when on. Gold filled when active. |
| Danger | `.btn .btn-danger` | Destructive only. |
| Small | add `.btn-sm` | Compact (padding & radius shrink). |

**Snippet:** [`components/button.html`](./components/button.html)

### Do
- Use exactly one `.btn-primary` per screen region.
- Pair `.btn-ghost` for "Cancel" beside a primary "Save".
- Animate state with class toggling (`active`), not inline styles.

### Don't
- Mix `.btn-primary` and `.btn-accent` in the same row (visual conflict).
- Override radius — it breaks the rhythm.

---

## Segmented Control — `.segmented`

A pill of mutually exclusive choices. Used in SchulterPlan for camera views (anterior / glenoid / lateral / inferior).

Anatomy: an outer `.segmented` flex container; inner `.seg-btn` items; exactly one carries `.active`. Each item has an SVG above a small uppercase label.

**Snippet:** [`components/segmented-control.html`](./components/segmented-control.html)

States: rest (muted text), hover (secondary text), active (surface bg + primary text + subtle shadow).

---

## Card — `.card`

The container that translucently floats over the surface.

Variants:
- `.card` — sidebar card, padding 14, radius 16.
- `.card-compact` — dashboard tile, padding 8 12, radius 12.
- `.card .card-header` — uppercase label strip inside a card.

**Snippet:** [`components/card.html`](./components/card.html)

Always combine with content components (e.g., `.measure-row`s).

---

## Implant Card — `.implant-card`

A selectable tile in the implant grid. Anchored by an inline SVG icon, two-line label, hover lift, selected ring.

States:
- rest → muted, hairline border.
- hover → teal border, soft-teal background, `translateY(-2px)`, icon color shifts.
- selected → ring (`0 0 0 3px var(--primary-glow)`), teal text, teal icon.

**Snippet:** [`components/implant-card.html`](./components/implant-card.html)

---

## Control Pad — `.control-row` + `.ctrl-btn`

A label-flanked-by-buttons row for incrementing/decrementing a value.

```
[−]  Depth        [+]
     0mm
```

- Grid `36px 1fr 36px`.
- `.ctrl-btn` is a 36×36 square button that turns teal on hover.
- The center `.ctrl-label` is a stack: big tabular value (`22px / 700`) over a tiny uppercase name (`9px / 500 / 1px tracking`).

**Snippet:** [`components/control-pad.html`](./components/control-pad.html)

---

## Arrow Pad — `.arrow-pad`

3×3 grid of `.ctrl-btn`s for 2D translation + axial rotation. Center is empty (separation).

**Snippet:** [`components/arrow-pad.html`](./components/arrow-pad.html)

---

## Measure Row — `.measure-row`

A label/value pair inside a card. Hairline divider between rows.

```
Retroversion   12.4°
```

Value is `14px / 700 / tabular-nums`. Use anywhere you display read-only metrics.

**Snippet:** [`components/measure-row.html`](./components/measure-row.html)

---

## Measure Item — `.measure-item`

A row inside the 3D measurement list. Anatomy: color dot + label + value + delete.

**Snippet:** [`components/measure-list.html`](./components/measure-list.html)

---

## Input / Textarea — `.input`

Universal input. Padding 10/14, radius 12, focus ring is the signature teal glow.

**Snippet:** [`components/input-textarea.html`](./components/input-textarea.html)

Apply to `<input>`, `<textarea>`, `<select>` alike.

---

## Toast — `.toast`

Glassy pill anchored bottom-center. Add the class `.show` to display. Auto-hide via `setTimeout` (see `js/toast.js`).

**Snippet:** [`components/toast.html`](./components/toast.html)

---

## Badge — `.badge`

Pill-shaped chip. Variants `.badge-accent` (gold), `.badge-primary` (teal).
Used for case info, status (LIVE), etc. Can include a `.live-dot` for animated indicators.

**Snippet:** [`components/badge.html`](./components/badge.html)

---

## Section Label — `.section-label`

Tiny uppercase sidebar header. **The most identity-defining text style in the system.**

```html
<div class="section-label">Implant Position</div>
```

11 px, weight 600, `text-transform: uppercase`, `letter-spacing: 1.2px`, color `--text-muted`,
`margin: 20px 0 10px` (first child drops top margin).

**Snippet:** [`components/section-label.html`](./components/section-label.html)

---

## Scenario Button — `.scenario-btn`

Full-width left-aligned tile for saved cases/scenarios. Add `.has-data` when populated to switch to teal ring.

**Snippet:** [`components/scenario-button.html`](./components/scenario-button.html)

---

## Topbar — `.topbar`

Always-on glassy header. Anatomy:
1. `.topbar-logo` — Implantcast PNG + gradient wordmark.
2. `.case-info` — pill chip with current case (or "No case loaded").
3. Optional link buttons (`.btn-flat .btn-sm`).
4. `.spacer` — pushes the rest right.
5. `.segmented` view switcher.
6. Action buttons (toggle on/off, primary action).

**Snippet:** [`components/topbar.html`](./components/topbar.html)

---

## Card Header — `.card-header`

The thin uppercase strip at the top of dashboard cards.

```html
<div class="card-header">3D Glenoid View</div>
```

Background is `rgba(0,0,0,0.2)` to "cut" the card visually.

---

## Live Dot — `.live-dot`

Pulsing green dot for AI / live indicators. Pair with a label.

```html
<span class="live-dot"></span> AI Listening
```

---

## State conventions (across all components)

| State | Visual rule |
|---|---|
| Default | Muted/secondary text, hairline border. |
| Hover | Border brightens to `--border-hover`, background to `--bg-card-hover`; primary buttons lift `-1px` and gain the teal glow. |
| Active (click) | `transform: scale(0.97)` for buttons, `scale(0.9)` for `.ctrl-btn`. |
| Selected / On | Teal ring (`box-shadow: 0 0 0 3px var(--primary-glow)`) for cards; solid gold + accent shadow for `.btn-accent`. |
| Focus | Replace outline with `box-shadow: 0 0 0 3px var(--primary-glow)` + `border-color: var(--primary)`. |
| Disabled | `opacity: 0.4; cursor: not-allowed; pointer-events: none;` |
| Loading | Prefer disabling + a `.live-dot` than a spinner. |

---

## When you need to invent a new component

1. Reach for an existing primitive first (button + card + section-label covers ~80% of cases).
2. If you must extend: copy the closest existing snippet, change as little as possible, and add an entry here before merging.
3. Stick to the token scale. Do not introduce a new radius, color, or duration.
