# Humerus Planning Page — `humerus.html`

Standalone page for 3D planning of the proximal humerus. Sibling to `test-heroui.html` (scapula) and `surgery-dashboard.html`. Single HTML file, Three.js via importmap, no build step.

> **Live URL when running locally:** http://localhost:8765/humerus.html
> **Entry points:** "Humerus" button in the topbar of `test-heroui.html` and `index.html`.

---

## 1. Layout

```
┌─ Topbar ────────────────────────────────────────────────────────────────────┐
│ [logo] SchulterPlan  [Humerus tag]  ← Scapula  [case]    Right view: [seg]  │
│                                                          [Showing Edited]   │
├──────────────┬──────────────────────────┬─────────────────────┬─────────────┤
│ Measurements │  Anterior viewport       │  Lateral viewport   │ Tools       │
│   • head r   │  (always anterior,       │  (switchable:       │ • Lasso     │
│   • CD angle │   fixed orientation)     │   lateral / ant.    │ • Undo/Rst  │
│   • canal Ø  │                          │   / superior /      │ • Measure   │
│   • cortical │  ╔══════════════════╗    │   inferior /        │ • Wireframe │
│              │  ║                  ║    │   medullary)        │ • Recenter  │
│ Comments     │  ║   humerus mesh   ║    │  ╔══════════════╗   │ • Medular   │
│              │  ║                  ║    │  ║              ║   │             │
│              │  ╚══════════════════╝    │  ╚══════════════╝   │             │
└──────────────┴──────────────────────────┴─────────────────────┴─────────────┘
```

- **Left sidebar** (280 px): 4 humerus measurements + Comments
- **Center**: two side-by-side viewports sharing one `BufferGeometry`
- **Right sidebar** (280 px): editing tools (lasso, undo, reset), measurement tool, display toggles

---

## 2. Feature catalogue

### 2.1 Two-viewport viewer

- **Left viewport** = always **anterior** (does not change).
- **Right viewport** = switchable via the topbar segmented control. Options: `lateral` (default), `anterior`, `superior`, `inferior`.
- Both meshes reference the **same** `THREE.BufferGeometry` instance. Edits propagate to both viewports automatically, no copying.
- Independent `WebGLRenderer`, `Scene`, `Camera`, `OrbitControls` per viewport. Rendering happens in one `requestAnimationFrame` loop.

### 2.2 Auto-orientation

The OBJ orientation is *not assumed*. At load time we:

1. Compute the geometry bounding box and `getSize()`.
2. Sort axes by length: **longest axis = humeral shaft**, mid axis, short axis.
3. Detect **which end** of the long axis carries the humeral head by comparing vertex counts in 8 %-thick slices at each extreme. The denser end is the head.
4. Stash `state.longAxis ∈ {'x','y','z'}` and `state.headEnd ∈ {+1, −1}`.

These two values drive every subsequent camera placement, the medullary cut plane, and the auto-measure routines.

### 2.3 View switcher (right viewport only)

Topbar segmented control with four buttons. Each one positions the right camera relative to the auto-detected axes:

| View | Camera direction | Up vector |
|---|---|---|
| `lateral` | along short axis | along long axis (head up) |
| `anterior` | along mid axis | along long axis (head up) |
| `superior` | along long axis from head side, looking down into the bone | mid axis |
| `inferior` | along long axis from distal side, looking up | mid axis |

While the **Medular** toggle is on, this segmented control is disabled.

### 2.4 Showing Edited / Showing Original toggle

A topbar button that swaps the geometry pointer of both meshes:

- `Showing Edited` (default): both meshes reference `state.editedGeometry`. Bone is the neutral `#eeeae0`.
- `Showing Original`: both meshes reference `state.originalGeometry`. Bone is tinted **blue** (`#b0c4e0`) to give an unmissable visual cue.

This **never** mutates data. It only changes which buffer is currently displayed. Independent from Undo and Reset.

### 2.5 "Remove Osteophytes" — Lasso tool

- Button activates lasso mode. While on:
  - Button label changes to **"Lasso Active — press Esc to exit"** and gains a gold inset border.
  - Viewports get a **gold lasso cursor** (inline SVG data URI).
  - OrbitControls are disabled in both viewports so dragging draws a polygon rather than rotating.
  - If the user was in "Showing Original" mode, the page snaps back to "Showing Edited" automatically.
- Drag in any viewport to draw a polygon. An SVG overlay shows the polyline.
- While dragging, the triangles whose centroids fall inside the lasso are **painted in semi-transparent red on the mesh in both viewports simultaneously** — the surgeon sees exactly what will be removed before releasing.
- Release the pointer to commit the removal.
- `Esc` cancels.

#### Performance (works on ~200 k–500 k triangle meshes)

- On `pointerdown`, all triangle centroids are projected to screen space ONCE (the camera is locked during a lasso drag).
- Subsequent `pointermove` events only run point-in-polygon against the cached 2D centroids (a 2-pass: bbox cull then ray-casting test).
- Highlight mesh rebuild is throttled with `requestAnimationFrame` so we render at most once per frame.

### 2.6 Three distinct "undo-like" controls

The user must be able to (a) step back one removal, (b) reset to original, and (c) compare before/after **without** any of them mutating data ambiguously.

| Control | What it does | Mutates data? |
|---|---|---|
| **Undo** (right sidebar) | Pops the top `Float32Array` from `state.undoStack` and restores it as the position attribute. Re-computes normals. `Cmd/Ctrl+Z` shortcut. | Yes — restores prior edit state. |
| **Reset** (right sidebar, danger style) | Confirms, then clones `state.originalGeometry` into `state.editedGeometry`, empties the undo stack. | Yes — irreversibly discards all edits. |
| **Showing Edited / Original** (topbar) | Swaps the geometry pointer of the two meshes. Doesn't touch `state.editedGeometry` at all. | **No** — pure visual toggle. |

### 2.7 Medullary axial cross-section ("Medular" button)

- Toggle in the right sidebar.
- ON:
  - Sets `vpL.renderer.clippingPlanes = [planeAtMidShaft]`. The plane normal points away from the head, constant = 0. Everything on the head side is clipped away.
  - Repositions the right camera above the head, looking along the long axis down to the cut surface.
  - Changes the right viewport label to `medullary · axial`.
  - Disables the view switcher segmented control.
- OFF: clears `vpL.renderer.clippingPlanes`, restores the camera to `state.rightView`.
- "Recenter Cameras" also exits Medular mode.

### 2.8 Measurement tool (3D distance)

Identical to the scapula page. Click two points on the mesh in either viewport → two spheres + connecting line + distance label in mm. List in the right sidebar with delete-per-item and Clear All. 6 rotating colors (`MEASURE_COLORS`).

### 2.9 Auto-compute measurements

Button in the left sidebar. Currently fills:

- **Head radius** — sphere fit (centroid + RMS) on the 18 % of vertices farthest along `+headEnd × longAxis`. Functional.
- **Medullary canal Ø** — heuristic ≈ 30 % of the mid-axis bbox size. Coarse approximation.
- **Cervico-diaphyseal angle** — placeholder. Proper calculation needs picked landmarks (head center, neck axis, shaft axis).
- **Cortical thickness** — placeholder.

Better measurements are TODO and depend on landmark-based interaction.

### 2.10 Other small bits

- **Wireframe** toggle (right sidebar).
- **Recenter Cameras** — fits both viewports to their current views; also exits Medular mode.
- **Comments** — text area + Post button. Stored in `state.comments` (in-memory).
- **Keyboard**: `Esc` cancels any active mode; `Cmd/Ctrl+Z` undoes.

---

## 3. State shape (single source of truth)

```js
const state = {
  // Geometries
  originalGeometry,    // immutable snapshot of loaded mesh (centered, non-indexed)
  editedGeometry,      // working geometry (positions only)
  undoStack,           // Float32Array[]  (max 50 entries)

  // Display
  showingOriginal,     // boolean — view toggle (not data)
  wireframe,
  rightView,           // 'lateral' | 'anterior' | 'superior' | 'inferior'
  medularMode,         // boolean — clipping plane on right viewport

  // Tools
  lassoMode, measureMode,
  lassoActiveVp,       // 'anterior' | 'lateral' while drawing
  lassoPoints,         // [{x,y}] screen px

  // Anatomy
  bbox, meshCenter, meshSize,
  longAxis,            // 'x'|'y'|'z'  — humeral shaft direction
  headEnd,             // +1 or -1     — which end of longAxis is the head

  comments,
};
```

---

## 4. Geometry pipeline

```
data/humerus.exported.obj
  → OBJLoader().load()
  → traverse() → first Mesh
  → toNonIndexed() if indexed
  → computeVertexNormals()
  → computeBoundingBox(), getSize(), getCenter()
  → translate(-center) — mesh now centered at origin
  → state.originalGeometry = geom.clone()
  → state.editedGeometry   = geom
  → detect longAxis & headEnd (vertex-density slice comparison)
  → build vpA.mesh and vpL.mesh, both with state.editedGeometry
  → fitCameraToView(vpA, 'anterior')
  → fitCameraToView(vpL, 'lateral')
```

Mesh is **always centered at origin**. Camera positions are derived purely from `state.meshSize`, `state.longAxis`, `state.headEnd`. Re-loading a different model simply repeats this pipeline.

---

## 5. Testing with another humerus model

### 5.1 Quick swap (no code changes)

1. Place your new OBJ in `data/`.
2. Rename it (or symlink it) to `data/humerus.exported.obj`.
3. Refresh `humerus.html` in the browser.

This is the simplest path — no edits required. The auto-detection pipeline handles arbitrary orientation, scale, and centering.

### 5.2 Multiple models side-by-side

If you want to keep several test models without renaming:

```
data/
  humerus.exported.obj          ← default (what humerus.html loads)
  humerus-test-patientA.obj
  humerus-test-pediatric.obj
  humerus-test-osteophytes.obj
```

Then in `humerus.html`, change one line (search for `loader.load(`):

```js
loader.load(
  'data/humerus-test-patientA.obj',   // ← change this URL
  (obj) => { ... }
```

Or wire a file picker (see § 5.5 below).

### 5.3 What the auto-detection needs to work

The model **must**:

- Be a watertight or near-watertight surface mesh in OBJ format.
- Be a single connected component (the OBJLoader only grabs the first mesh inside the file).
- Have a clear long axis — the cross-section must be visibly narrower in the shaft than at the humeral head. (Pediatric / non-canonical bones may need manual tweaking.)
- Be in any reasonable scale (mm preferred, but the page only displays distances in mm without unit conversion — so a meter-scale OBJ will read as "1500 mm" instead of "1.5 m").

The model **does NOT need to**:

- Be in any specific axis convention (X / Y / Z up — all auto-detected).
- Be centered (auto-centered at load).
- Be triangulated with indexed buffers (auto-converted to non-indexed).
- Carry normals (auto-computed).

### 5.4 Per-model knobs (rare cases)

If auto-detection misbehaves on a model:

| Symptom | Knob | Where |
|---|---|---|
| Anterior view shows side of bone instead of front | `midAxis` heuristic picked wrong mid axis | `fitCameraToView()` — swap manually for that model |
| Head appears down in all views | `state.headEnd` wrong | The slice-counting heuristic mis-fired; flip sign manually |
| Auto-measure head radius way off | The 18 % vertex window misses the actual head | `computeHeadRadius()` — adjust the `0.18` literal |
| Medular plane doesn't intersect the canal cleanly | The model isn't centered on its anatomical mid-shaft | `buildMedularPlane()` — adjust the `0` constant |

### 5.5 Optional — file picker UI

Not implemented today; to add one:

```html
<!-- inside the topbar -->
<input type="file" id="humerus-file" accept=".obj" style="display:none" />
<button class="btn btn-ghost btn-sm" onclick="document.getElementById('humerus-file').click()">
  Load OBJ…
</button>
```

```js
document.getElementById('humerus-file').addEventListener('change', (e) => {
  const f = e.target.files?.[0]; if (!f) return;
  const fr = new FileReader();
  fr.onload = () => {
    const obj = new OBJLoader().parse(fr.result);
    if (vpA.mesh) { vpA.scene.remove(vpA.mesh); vpL.scene.remove(vpL.mesh); }
    if (state.editedGeometry)   state.editedGeometry.dispose();
    if (state.originalGeometry) state.originalGeometry.dispose();
    state.undoStack = [];
    processLoadedOBJ(obj);   // extract the load callback into this function first
    document.getElementById('case-info').textContent = f.name;
  };
  fr.readAsText(f);
});
```

This is a 10-minute addition when needed.

---

## 6. Known limitations / future work

- [ ] Auto-compute of **cervico-diaphyseal angle** and **cortical thickness** — needs landmark picking UI.
- [ ] **Export edited mesh** as OBJ (useful for downstream prosthesis fitting).
- [ ] **Save / load planning sessions** to `localStorage` or server (current state is lost on refresh).
- [ ] **Stencil-buffer fill** of the medullary cross-section so the cut surface reads as a solid 2D outline rather than a clipped hole.
- [ ] **Symmetric humerus generation** — mirror the contralateral side for comparison.
- [ ] **Refined view-switcher icons** — current SVGs are placeholders.
- [ ] **File picker** for loading other OBJ models without code changes (§ 5.5).

---

## 7. Quick reference — keyboard shortcuts

| Key | Action |
|---|---|
| `Esc` | Cancel active mode (lasso or measure) |
| `Cmd/Ctrl + Z` | Undo last osteophyte removal |

---

## 8. File locations

| File | Purpose |
|---|---|
| `humerus.html` | The page itself (HTML + CSS + JS inline, ~1500 lines) |
| `data/humerus.exported.obj` | Default model loaded on page open (~12 MB) |
| `data/logo_implantcast.png` | Topbar logo |
| `CLAUDE.md` | Project memory — also mentions this page |
| `CHANGELOG.md` | Per-session changes |
| `HUMERUS.md` | This document |
