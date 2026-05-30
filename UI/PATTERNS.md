# Patterns

Recurring compositions. When you need a screen, start here.

---

## P1 — Three-column app shell (Planner)

```
┌────────────────────────────────────────────────────────────┐
│ Topbar (glass)                                             │  60 px
├──────────┬─────────────────────────────────┬───────────────┤
│ Sidebar  │     Main canvas / viewer        │ Right sidebar │
│ left     │     (3D, chart, anything)       │ (controls)    │
│ 280 px   │                                 │ 290 px        │
└──────────┴─────────────────────────────────┴───────────────┘
```

Use for: planners, editors, IDEs, anywhere the user manipulates a primary canvas while configuring it on either side.

Template: `templates/planner-3col-layout.html`.

### Section ordering — left sidebar

1. Pre-Op Measurements (read-only metrics, `.measure-row`s in a `.card`)
2. Implant / Item Selection (grid of `.implant-card`s)
3. Saved Scenarios (`.scenario-btn` list)
4. Actions stack (`Save`, `Export`, `Share`)

### Section ordering — right sidebar

1. Primary controls (the most-used adjustments)
2. Translation pad (`.arrow-pad`)
3. Read-only summary card (`.measure-row`s reflecting current state)
4. Reset action
5. Domain-specific visualizations (e.g., contact map)
6. Measurements (tool + list)
7. Comments (textarea + button)

This left→right ordering mirrors the user's cognitive flow: *select → adjust → review → annotate*.

---

## P2 — Dashboard shell (TV / monitor)

```
┌────────────────────────────────────────────────────────────┐
│ Topbar  [logo] [LIVE badge] [patient info]    [Back link]  │  52 px
├──────────┬───────────────┬───────────────┬───────────────┐ │
│ Side     │ Viewport      │ Viewport      │ Viewport      │ │
│ panel    ├───────────────┼───────────────┼───────────────┤ │
│ 180 px   │ Viewport      │ Viewport      │ Viewport      │ │
├──────────┴───────────────┴───────────────┴───────────────┤ │
│                                              AI panel    │ │
│                                              240 px      │ │
└────────────────────────────────────────────────────────────┘
```

Use for: at-a-glance multi-viewport displays, surgical TV, watch-only dashboards.

Template: `templates/dashboard-layout.html`.

---

## P3 — Section block

Every sidebar (and most cards) is a stack of *section blocks*:

```html
<div class="section-label">Implant Position</div>
<div class="card">
  <!-- content -->
</div>
```

Optional trailing `<div class="divider"></div>` separates the block from the next.

---

## P4 — Metric card

A small card that lists 2–4 labeled values:

```html
<div class="card">
  <div class="measure-row">
    <span class="label">Retroversion</span>
    <span class="value">12.4°</span>
  </div>
  <div class="measure-row">
    <span class="label">Inferior Incl.</span>
    <span class="value">8.1°</span>
  </div>
</div>
```

Use anywhere you want to communicate "these numbers go together".

---

## P5 — Selectable grid

A 2-column grid of selectable tiles (implant cards). Pattern works for any catalog (sizes, models, prosthesis options, scenarios).

```html
<div class="implant-group-label">Glenoid Cementless Anatomical</div>
<div class="implant-grid">
  <div class="implant-card selected">…</div>
  <div class="implant-card">…</div>
  <div class="implant-card">…</div>
  <div class="implant-card">…</div>
</div>
```

For 1-column lists, prefer `.scenario-btn`s in a `.scenario-list`.

---

## P6 — Control trio

The canonical pattern for "decrement / value / increment":

```html
<div class="control-row">
  <button class="ctrl-btn">−</button>
  <div class="ctrl-label">
    <div class="name">Depth</div>
    <div class="value">0mm</div>
  </div>
  <button class="ctrl-btn">+</button>
</div>
```

Stack multiple control-rows vertically with no extra wrapper.

---

## P7 — Translation pad

3×3 grid of arrow controls. Center cell is intentionally empty; bottom-left/right are reserved for rotation.

See template `components/arrow-pad.html` (canonical Implantcast layout).

---

## P8 — Action stack

At the bottom of a sidebar section:

```html
<div class="actions-stack">
  <button class="btn btn-primary w-full">Save</button>
  <button class="btn btn-ghost w-full">Save to Server</button>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
    <button class="btn btn-ghost btn-sm">Export</button>
    <button class="btn btn-ghost btn-sm">Share</button>
  </div>
</div>
```

Primary action gets full width and is visually unique. Secondary actions are equal weight.

---

## P9 — Annotation block

For comments / notes:

```html
<div class="section-label">Comments</div>
<div id="comments-list" style="font-size:12px;color:var(--text-muted);margin-bottom:8px">
  No comments yet.
</div>
<textarea class="input" rows="2" placeholder="Add a comment…"></textarea>
<button class="btn btn-flat btn-sm w-full" style="margin-top:6px">Post Comment</button>
```

Empty state is a single muted sentence (no illustration).

---

## P10 — Toast invocation

Toast lives at the bottom-center. Trigger via `showToast('Case loaded.')` (see `js/toast.js`).

Rules:
- Always full sentences ending in a period.
- Auto-dismiss after 2.5 s.
- One toast at a time — replace, don't queue.
