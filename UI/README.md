# SchulterPlan UI — Design System Package

**Purpose:** This folder is a self-contained design system kit. Drop it into any front-end or back-end project (React, Vue, Svelte, plain HTML, Next.js, etc.) and reproduce the exact look & feel of the SchulterPlan application — by Dr. Bruno Gobbato (Implantcast Edition).

> If you are an AI agent reading this folder to build something new: **start with `AGENT_INSTRUCTIONS.md`**.

---

## What's inside

```
UI/
├── README.md                  ← you are here
├── AGENT_INSTRUCTIONS.md      ← how an LLM should consume this folder
├── DESIGN_SYSTEM.md           ← the full spec (colors, type, spacing, motion, voice)
├── BRAND.md                   ← brand identity, voice, what SchulterPlan "feels like"
├── COMPONENTS.md              ← anatomy of every component (props, states, do's & don'ts)
├── PATTERNS.md                ← layout patterns, screens, common compositions
├── ACCESSIBILITY.md           ← contrast, focus, keyboard, screen-reader notes
│
├── tokens/
│   ├── tokens.css             ← all design tokens as :root CSS variables
│   ├── tokens.json            ← same tokens, machine-readable (for Tailwind/SCSS/Style-Dictionary)
│   └── tokens.scss            ← SCSS variables
│
├── css/
│   ├── base.css               ← reset + typography + body
│   ├── layout.css             ← .app, .topbar, .sidebar, .viewer grid
│   ├── components.css         ← .btn, .card, .input, .segmented, .ctrl-btn ...
│   ├── schulterplan.css       ← single-file bundle (drop-in stylesheet)
│   └── tailwind.config.cjs    ← Tailwind preset mirroring the tokens
│
├── components/                ← HTML snippets — copy/paste into any framework
│   ├── topbar.html
│   ├── button.html
│   ├── segmented-control.html
│   ├── card.html
│   ├── implant-card.html
│   ├── control-pad.html
│   ├── arrow-pad.html
│   ├── measure-row.html
│   ├── measure-list.html
│   ├── input-textarea.html
│   ├── toast.html
│   ├── scenario-button.html
│   └── section-label.html
│
├── templates/
│   ├── planner-3col-layout.html  ← the main planner shell (sidebar / viewer / sidebar)
│   └── dashboard-layout.html     ← the surgery dashboard shell
│
├── examples/
│   ├── kitchen-sink.html         ← every component in one preview page
│   └── minimal-app.html          ← smallest possible app applying the system
│
├── js/
│   ├── toast.js                  ← showToast() helper
│   ├── theme.js                  ← attaches tokens to documentElement at runtime
│   └── ui-helpers.js             ← small DOM helpers used by demo HTMLs
│
├── assets/
│   └── README.md                 ← where to drop logo_implantcast.png etc.
└── icons/
    └── README.md                 ← inline SVG icon reference (anterior/glenoid/lateral/inferior)
```

---

## 60-second start (vanilla HTML)

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <link rel="stylesheet" href="UI/css/schulterplan.css" />
</head>
<body>
  <button class="btn btn-primary">Save</button>
  <button class="btn btn-ghost">Cancel</button>
</body>
</html>
```

That's it. Everything else is conventions, examples, and documentation to keep the look consistent across projects.

---

## 60-second start (React)

```jsx
import 'UI/css/schulterplan.css';

export function PrimaryButton({ children, onClick }) {
  return <button className="btn btn-primary" onClick={onClick}>{children}</button>;
}
```

You do **not** need to rewrite the design as JSX components — the CSS class API is the contract.

---

## 60-second start (Tailwind project)

Copy `UI/css/tailwind.config.cjs` into your project root (merge with your existing `tailwind.config.js`). All tokens are exposed as Tailwind utilities:

```html
<button class="bg-primary text-black rounded-md px-4 py-2 hover:shadow-glow">Save</button>
```

---

## The non-negotiables

These define SchulterPlan visually. If a downstream project breaks any of them, it stops looking like SchulterPlan:

1. **Dark background** — `#000` base, `#18181b` surface. No light theme yet.
2. **Inter font** — 300–800 weights, antialiased.
3. **Implantcast teal as primary** — `#17c5b0`, with a glow shadow for emphasis.
4. **Gold as accent** — `#f5a623` for toggle-on / active accent states.
5. **Glassmorphism on the topbar & toasts** — `backdrop-filter: blur(16px)` over translucent zinc.
6. **Generous radii** — 8/12/16/24 px. Nothing sharp.
7. **Tabular numerals on every metric** — `font-variant-numeric: tabular-nums`.
8. **Tight, uppercase section labels** — 11px, weight 600, letter-spacing 1.2px, muted color.
9. **Cards on cards** — translucent `rgba(39,39,42,0.7)` over the dark base, hairline `1px` border at 8% white opacity.
10. **Motion is subtle** — `0.2s cubic-bezier(0.4, 0, 0.2, 1)`, micro `translateY(-1px)` on hover, `scale(0.97)` on press.

---

## Provenance

Extracted from the production SchulterPlan app:

- Live: <https://schulterplan.vercel.app/>
- Repository: <https://github.com/bgobbato/schulterplan>
- Source files: `test-heroui.html`, `surgery-dashboard.html`
- Inspired by HeroUI / NextUI dark theme conventions.

---

**Author:** Dr. Bruno Gobbato
**Edition:** Implantcast
**Version:** 1.0 (May 2026)
