# Brand — SchulterPlan

> What SchulterPlan **feels** like. Use this as a litmus test: if a screen feels wrong, it probably breaks something here.

---

## Identity

**SchulterPlan** is a 3D shoulder-arthroplasty planner built by **Dr. Bruno Gobbato**, in the **Implantcast** edition. It targets orthopedic surgeons and the operating room.

- **Schulter** = "shoulder" in German — a nod to Implantcast's origin.
- **Plan** = the act of planning before the procedure.

The product is **clinical, precise, calm**. It is **not** a consumer app, not a game, not a marketing site. It looks expensive without being decorative.

---

## Personality

| Is | Is not |
|---|---|
| Quiet | Loud |
| Precise | Approximate |
| Confident | Apologetic |
| Technical | Marketing |
| Dark, focused | Bright, breezy |
| German engineering | Silicon Valley product |
| Minimal | Bare |

If a button or screen would feel at home on Stripe, Linear, or Vercel — keep going. If it would feel at home on a B2C SaaS landing page with gradients and emojis — back up.

---

## Voice & tone

Default to **English**. Portuguese is acceptable in internal/admin contexts (the author is Brazilian).

### Microcopy rules

1. **Verbs, not nouns.** "Save Current Scenario", "Import Case", "Reset Position".
2. **No exclamation marks.** Ever.
3. **No emojis** in UI chrome. (Two exceptions exist in the current app: 🦴 viewer empty state and 📏 Measure tool. These are deliberate and small.)
4. **No hype words.** "Beautiful", "Amazing", "Awesome", "Just" — all banned.
5. **Numbers are facts.** "16.1 mm inferior" — never "about 16 mm".
6. **Errors describe what happened, not what feels.** "No case loaded" — not "Oops, no case yet!".
7. **Toasts are full sentences with a period.**
8. **Tooltips are noun phrases or imperative fragments, no period.**

### Examples — good vs. bad

| ✅ | ❌ |
|---|---|
| "Save Current Scenario" | "Save your scenario! ✨" |
| "Import Case" | "Get started — upload a case" |
| "No comments yet." | "Nothing here yet 🤷" |
| "Center Line" | "Show The Center Line" |
| "Click two points on the 3D model" | "Click somewhere to start measuring!" |

### Length

- Buttons: 1–3 words.
- Tooltips: ≤ 8 words.
- Toasts: 1 sentence, ≤ 80 chars.
- Section labels: 1–3 words, uppercase.

---

## Visual signature

The three things that make a screenshot identifiable as SchulterPlan:

1. **Black canvas + zinc cards + 1-px hairlines** — the substrate.
2. **Teal as the only saturated color** — used sparingly: primary buttons, focus rings, selected implants, key metrics.
3. **Tiny uppercase section labels with letter-spacing** — they look like callouts in a German engineering datasheet.

If you remove any of these three, the product no longer reads as SchulterPlan.

---

## Wordmark

- "SchulterPlan" — single word, camel-case.
- Set in Inter 700 with a linear gradient: `linear-gradient(135deg, var(--primary), #7dd3fc)` clipped to the text.
- Always sits beside the Implantcast logo (`logo_implantcast.png`, 28–32 px tall) in the topbar.
- Never apply effects beyond the gradient (no shadow, no outline, no animation).

---

## Logo lock-up

```
[ic logo 32px]  SchulterPlan
                ↑ Inter 700, teal→sky gradient, -0.3px tracking
```

Spacing between logo and wordmark: `10px`.

---

## Photography & imagery

- The "hero image" of SchulterPlan is always **the 3D scapula + implant viewport**.
- Never use stock photos.
- Never use illustrations of doctors / hospitals.
- Custom SVG icons for implants are part of the system (see `components/implant-card.html`).

---

## Author signature

A discrete credit appears bottom-right of the planner, 10 px, 40% opacity, never animated:

```
SchulterPlan — implantcast
Created by Dr. Bruno Gobbato
```

Do not remove this in derivative projects without permission.

---

## When in doubt

Open <https://schulterplan.vercel.app/>. If your screen does not feel like the same product, something is off.
