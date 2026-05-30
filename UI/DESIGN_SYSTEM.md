# Design System — SchulterPlan

> The full specification. Every value here lives in `tokens/tokens.css`. This document explains **why** each choice exists.

---

## 1. Foundation

### 1.1 Inspiration
The system is derived from **HeroUI / NextUI dark theme** conventions, adapted for clinical use:

- Pure-black background (operating-room-friendly contrast, OLED-economical).
- Translucent zinc surfaces (depth without distraction).
- Implantcast teal as the brand thread (`#17c5b0`).
- Gold (`#f5a623`) as a discrete, attention-grabbing accent for toggles.

### 1.2 Philosophy

| Principle | Manifestation |
|---|---|
| **Quiet by default** | Muted text colors, hairline borders, low-saturation surfaces. |
| **Loud where it matters** | Teal glow on hover, gold solid on active toggles, tabular metrics. |
| **Calm motion** | One easing curve, one duration. No spring physics, no bouncing. |
| **Surgical precision** | Tabular numerals, fixed radii, tight uppercase labels. |
| **Glass over solid** | Topbar, toasts and dialogs use `backdrop-filter`. Sidebars are solid. |

---

## 2. Color

### 2.1 Surfaces

| Token | Value | Usage |
|---|---|---|
| `--bg-base` | `#000000` | Planner page background. |
| `--bg-base-alt` | `#0a0a0f` | Dashboard page background (slightly lifted to compete less with bright 3D viewports). |
| `--bg-surface` | `#18181b` | Sidebars, opaque panels. |
| `--bg-card` | `rgba(39,39,42,0.7)` | Translucent cards over `--bg-surface`. |
| `--bg-card-hover` | `rgba(63,63,70,0.5)` | Card / ghost-button hover. |
| `--bg-glass` | `rgba(24,24,27,0.6)` | Topbar, toasts — receives `backdrop-filter: var(--blur)`. |

### 2.2 Text

| Token | Value | Usage |
|---|---|---|
| `--text-primary` | `#fafafa` | Main copy, metric values. |
| `--text-secondary` | `#a1a1aa` | Labels, secondary copy, ghost-button rest state. |
| `--text-muted` | `#71717a` | Section labels, placeholder, disabled, helper. |

### 2.3 Brand

| Token | Value | Usage |
|---|---|---|
| `--primary` | `#17c5b0` | Implantcast teal — primary buttons, focus rings, key actions, selected implant cards. |
| `--primary-hover` | `#14b8a6` | Hover state on `--primary` solid surfaces. |
| `--primary-glow` | `rgba(23,197,176,0.25)` | Used in `box-shadow` for the signature teal glow. |
| `--primary-soft` | `rgba(23,197,176,0.12)` | Flat / tinted button backgrounds. |
| `--accent` | `#f5a623` | Gold — toggleable controls (Implant On). |
| `--accent-soft` | `rgba(245,166,35,0.12)` | Resting state of accent buttons. |
| `--accent-glow` | `rgba(245,166,35,0.30)` | Shadow under active gold buttons. |

### 2.4 Semantic

| Token | Value | Usage |
|---|---|---|
| `--danger` | `#f31260` | Delete actions, errors, destructive hover on `.measure-delete`. |
| `--success` | `#17c964` | Success toasts, "near contact" legend. |
| `--warning` | `#f5a524` | Warnings (shares hue with accent but only used for status). |
| `--info` | `#7dd3fc` | Logo gradient endpoint. |

### 2.5 Domain — Contact Heat Map

These colors are specific to the bone-contact analysis canvas but follow the brand:

| Token | Value | Meaning |
|---|---|---|
| `--contact-embedded` | `#1e78c8` | Implant past bone surface (depth < −1 mm). |
| `--contact-surface` | `#008232` | Direct contact (−1 mm ≤ depth ≤ 0). |
| `--contact-near` | `#17c964` | Gap < 0.5 mm. |
| `--contact-none` | `#3c3c41` | No contact. |

### 2.6 Domain — 3D Measurement Rotation

Six rotating colors for measurement spheres. Always cycle in this order:

`cyan → orange → yellow → purple → green → pink → cyan …`

```
#00ccff, #ff6644, #ffcc00, #cc44ff, #44ff88, #ff4488
```

---

## 3. Typography

### 3.1 Family
**Inter** — loaded from Google Fonts, weights 300–800.
Fallback chain: `Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`.

### 3.2 Scale

| Token | Size | Common usage |
|---|---|---|
| `--fs-xxs` | 9 px | View-button labels under icons. |
| `--fs-xs` | 10 px | Implant card labels, dashboard card headers. |
| `--fs-sm` | 11 px | Section labels, legends, hints. |
| `--fs-base` | 12 px | Scenarios, secondary text, badges. |
| `--fs-md` | 13 px | Buttons, inputs, measure rows. |
| `--fs-lg` | 14 px | Values in measure rows. |
| `--fs-xl` | 16 px | Logo wordmark. |
| `--fs-2xl` | 18 px | Percent symbol on contact map. |
| `--fs-3xl` | 22 px | Big metric value in control labels. |
| `--fs-4xl` | 32 px | Contact-percentage hero number. |

### 3.3 Weights

- 300/400 — body copy (rare in this system).
- 500 — buttons, ghost text.
- 600 — section labels, segmented active, implant cards.
- 700 — values, headings, primary metric.
- 800 — reserved.

### 3.4 Letter-spacing

| Token | Value | Where |
|---|---|---|
| `--tracking-tight` | `-0.3px` | Logo wordmark. |
| `--tracking-section` | `1.2px` | Uppercase section labels (`.section-label`). |
| `--tracking-kbd` | `1px` | Tiny labels under ctrl-label values. |
| `--tracking-tag` | `0.5px` | Implant-card text, view-button labels. |

### 3.5 Numerals
**Always** apply `font-variant-numeric: tabular-nums` to:
- Measure values (`.measure-row .value`)
- Ctrl-label values (`.ctrl-label .value`)
- Contact percentage
- Any value that updates while the user manipulates a control

This is non-negotiable — proportional numerals jitter and look amateur.

---

## 4. Spacing

8-px informal base. Values map to the `--space-N` scale (see `tokens.css`).
Most paddings & gaps in components round to: **4, 6, 8, 10, 12, 14, 16, 20, 24, 32**.

Component-level conventions:
- Card padding: `14px`.
- Sidebar padding: `20px`.
- Topbar horizontal padding: `20px`.
- Section-label vertical rhythm: `margin: 20px 0 10px` (the first one drops the top margin).

---

## 5. Radii

| Token | Value | Used by |
|---|---|---|
| `--radius-sm` | 8 px | `.btn-sm`, measure list items. |
| `--radius-md` | 12 px | `.btn`, inputs, ctrl-btn, cards in dashboard. |
| `--radius-lg` | 16 px | Cards in sidebar. |
| `--radius-xl` | 24 px | Toasts. |
| `--radius-pill` | 999 px | `.case-info` chip, badges. |

Nothing is sharp. Avoid `border-radius: 0` or `4px`.

---

## 6. Borders

- `1px solid var(--border)` — all hairlines, 8% white.
- `1.5px solid var(--border)` — implant cards (slightly heavier for clickability).
- `2px` — focus rings replace with `box-shadow: 0 0 0 3px var(--primary-glow)` instead.

---

## 7. Shadows

| Token | Value | Where |
|---|---|---|
| `--shadow-sm` | `0 2px 8px rgba(0,0,0,0.30)` | Cards, scenarios. |
| `--shadow-md` | `0 4px 16px rgba(0,0,0,0.40)` | Tooltips. |
| `--shadow-lg` | `0 8px 32px rgba(0,0,0,0.50)` | Toasts. |
| `--shadow-glow` | `0 0 20px var(--primary-glow)` | Primary button hover. |
| `--shadow-accent` | `0 0 16px var(--accent-glow)` | Accent button active. |

**The teal glow is the signature.** Use it on the most important call-to-action of any screen.

---

## 8. Motion

One easing curve, two durations:

```css
--ease:            cubic-bezier(0.4, 0, 0.2, 1);
--transition:      0.2s var(--ease);  /* default */
--transition-slow: 0.3s var(--ease);  /* toasts, dialogs */
```

Conventions:
- **Hover lift**: `.btn-primary` translates `-1px` on `:hover`.
- **Press**: every button (`.btn`, `.ctrl-btn`) scales `0.97` on `:active`.
- **Card hover**: border brightens to `--border-hover`, background to `--bg-card-hover`.
- **Toast**: enters via `translateY(12px) → 0` with opacity 0→1 over 0.3s.

Avoid: spring physics, parallax, anything > 0.4s.

---

## 9. Glass effect

Apply on `.topbar`, `.toast`, and any future modal/popover:

```css
background: var(--bg-glass);
backdrop-filter: var(--blur);
-webkit-backdrop-filter: var(--blur);
border-bottom: 1px solid var(--border);  /* directional */
```

Always include the `-webkit-` prefix for Safari.

---

## 10. Focus & accessibility

Default focus style across inputs and buttons:
```css
box-shadow: 0 0 0 3px var(--primary-glow);
border-color: var(--primary);
outline: none;
```

Do not remove focus outlines without providing the teal ring replacement.
Minimum contrast on body text: `--text-secondary` over `--bg-base` ≈ 8:1 ✅.

See `ACCESSIBILITY.md`.

---

## 11. Iconography

- SVG inline, `stroke="currentColor" fill="none"` for outline icons, `fill="currentColor"` for filled.
- Stroke width 2, line-cap and line-join rounded.
- Standard icon size in buttons: `14×14`.
- Standard icon size in segmented control: `18×18`.

The view-switcher icons (anterior/glenoid/lateral/inferior) are bespoke — see `icons/README.md`.

---

## 12. Layout primitives

### 12.1 Planner shell (`app`)

```
grid-template-columns: 280px 1fr 290px;
grid-template-rows:    60px 1fr;
```

Row 1 spans all columns (topbar). Row 2 is `[sidebar | viewer | sidebar]`.

### 12.2 Dashboard shell

```
grid-template-rows:    52px 1fr;
grid-template-columns: 1fr 240px;
```

The main content area is itself a `4-col × 2-row` grid for the 6 viewports + humerus panel.

### 12.3 Responsive

Below 768 px: stack vertically. Sidebars become full-width panels stacked under the topbar; the viewer collapses to a 240–360 px frame; implant grid becomes 3 columns.

---

## 13. Voice & microcopy

(See `BRAND.md` for the full take.)

- **Imperative, short.** "Save", "Import Case", "Reset Position".
- **No exclamation marks.** Clinical tools don't shout.
- **English by default.** Portuguese is acceptable for internal tooling.
- **Tooltips end without a period.**
- **Toasts are sentences with a period.**

---

## 14. What you may **not** add

- Light theme variants (defer until explicitly requested).
- Gradients other than the logo's teal→sky.
- Saturated reds/oranges outside semantic tokens.
- Sans-serif fonts other than Inter.
- Border-radius values not on the scale (e.g., 4 px, 10 px).
- Easing curves other than the documented one.
