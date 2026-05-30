# Accessibility

The SchulterPlan system targets **WCAG 2.1 AA** at minimum. Below: what to verify, what we already cover, and what every downstream project must preserve.

---

## Contrast (computed against `#000000` base)

| Token | Contrast | WCAG |
|---|---|---|
| `--text-primary` `#fafafa` | ~20:1 | AAA |
| `--text-secondary` `#a1a1aa` | ~7.6:1 | AAA (body) / AA (large) |
| `--text-muted` `#71717a` | ~4.6:1 | AA large only — never use for body copy. |
| `--primary` `#17c5b0` | ~7.2:1 | AAA |
| `--accent` `#f5a623` | ~9.4:1 | AAA |
| `--danger` `#f31260` | ~4.6:1 | AA large only |
| `--success` `#17c964` | ~7.4:1 | AAA |

### Rules
- Never use `--text-muted` for sentences. Restrict to labels ≥ 11 px **and** weight 600 (uppercase section labels qualify).
- Never combine `--danger` with body copy. Use it as fill on buttons (`#fff` on `#f31260` is AA).

---

## Focus

We disable the default browser outline and replace it with our teal ring:

```css
.input:focus,
.btn:focus-visible {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-glow);
}
```

Every interactive element must be reachable via keyboard and must show this ring when focused. Add `:focus-visible` to buttons if your downstream tooling supports it.

---

## Keyboard

- All `.btn`, `.ctrl-btn`, `.seg-btn`, `.implant-card`, `.scenario-btn` must be native `<button>` (or have `role="button"` + `tabindex="0"` + key handlers).
- Tab order follows the DOM. Sidebars come before the canvas.
- Provide `Esc` to exit any "modal-like" mode (e.g., measurement mode).
- Provide arrow-key support on the translation pad (mirroring its buttons).

---

## Screen readers

- Use `aria-label` on icon-only buttons:
  ```html
  <button class="ctrl-btn" aria-label="Increase depth">+</button>
  ```
- Use `aria-pressed="true|false"` on toggleable accent buttons (`Implant On`, `Transparent`, etc.).
- Use `role="status"` (or `aria-live="polite"`) on the toast container so notifications are announced.
- Decorative SVG icons: `aria-hidden="true"`. Meaningful icons: provide a `<title>`.

---

## Motion

We honor `prefers-reduced-motion: reduce` globally:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Do not introduce parallax, auto-playing video, or > 0.4 s animations.

---

## Touch targets

- `.ctrl-btn` is 36×36 px — exactly at the iOS minimum touch target threshold; do not shrink.
- `.btn` is ≥ 32 px tall — comfortable.
- `.btn-sm` is smaller (28 px) — only use in dense toolbars, never as a primary mobile action.

---

## Form labels

Always pair a `<label>` (or `aria-label`) with `.input`. The placeholder is not a label.

---

## Reduced color / high contrast

If the OS reports `forced-colors: active` (Windows high contrast), do not rely on the teal/gold to convey meaning. The `border` + uppercase label hierarchy must still communicate structure.

---

## Test checklist before shipping

- [ ] Tab through the entire page. Every actionable element shows the teal focus ring.
- [ ] `Esc` exits transient modes.
- [ ] All icon-only buttons have `aria-label`.
- [ ] Toggle buttons announce state via `aria-pressed`.
- [ ] Toast updates are announced (`aria-live="polite"` on container).
- [ ] Color is never the sole signal — pair with text/icon/state.
- [ ] `prefers-reduced-motion: reduce` flattens animations.
- [ ] Body copy is never `--text-muted`.
