# Icons

The SchulterPlan UI uses **inline SVG** rather than icon fonts or sprite sheets. This keeps icons:
- Vector-perfect at any size.
- `currentColor`-tintable (matches the surrounding text).
- Zero extra HTTP requests.

## Conventions

- `viewBox="0 0 24 24"` for general icons.
- Outline icons: `fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"`.
- Filled icons: `fill="currentColor"`.
- Size at the call site (`width`/`height` attribute or CSS).
- Decorative: `aria-hidden="true"`. Meaningful: include a `<title>` child.

## Sizes used in the system

| Context | Size |
|---|---|
| Inside `.btn-flat .btn-sm` | 14×14 |
| Inside `.btn` | 16×16 (rare) |
| Inside `.seg-btn` | 18×18 |
| Inside `.card-header` (e.g., AI logo) | 14×14 |

---

## Canonical inline SVGs

### View switcher (4 bespoke icons)

```html
<!-- anterior -->
<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L8 6v6l-2 2v6l4-2 2 2 2-2 4 2v-6l-2-2V6l-4-4z"/></svg>

<!-- glenoid -->
<svg viewBox="0 0 24 24" fill="currentColor"><ellipse cx="12" cy="12" rx="6" ry="9"/></svg>

<!-- lateral -->
<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 2v6l-3 3v6l3 5h-4l-2-5v-6l2-3V2z"/></svg>

<!-- inferior -->
<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 22l-4-4h3V10H8l4-4 4 4h-3v8h3z"/></svg>
```

### Dashboard (4-pane grid)

```html
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <rect x="3" y="3" width="7" height="9"/>
  <rect x="14" y="3" width="7" height="5"/>
  <rect x="14" y="12" width="7" height="9"/>
  <rect x="3" y="16" width="7" height="5"/>
</svg>
```

### Info "i" (tooltip trigger)

```html
<span class="info-icon" style="
  display:inline-flex; align-items:center; justify-content:center;
  width:18px; height:18px; border-radius:50%;
  border:1px solid var(--text-muted); color:var(--text-muted);
  font-size:11px; font-weight:600; cursor:help;
">i</span>
```

### Implant SVGs

Each implant card uses a bespoke SVG schematic of the prosthesis. See the implant SVGs in the source `test-heroui.html` (lines ~710–830) or copy from `components/implant-card.html`. These are part of the brand language — re-use them rather than authoring new shapes.

---

## When you must introduce a new icon

1. Prefer authored 24×24 SVG over a library.
2. Match outline / fill style of neighboring icons.
3. Inline it — do not introduce an icon library dependency.
4. If you do reach for a library, **Lucide** is the closest match in style. Pin exact icons in a small wrapper component; do not ship the whole pack.
