# MPR (CT) Implementation Plan — Multi-Planar Reconstruction

**Status**: Planned — not yet implemented
**Last updated**: 2026-05-29
**Target page**: `test-heroui.html` (scapula planner)

## Goal

Add a vertical column on the right side of the scapula planner viewer showing
3 CT slices (axial top, coronal middle, sagittal bottom), toggled by a `CT`
button in the topbar. The implant must appear as an outline overlay in each
slice, in the exact 3D position the surgeon planned.

## Safety strategy — don't break current project

The current project works. We MUST be able to revert if MPR experiments break
anything. Two layers of safety:

### Layer 1 — Git backup branch (do FIRST)

```bash
cd "/Users/brunogobbato/Dropbox/Claude Workspace/Advita/gps-web-planner Implantcast"
git checkout -b mpr-experiment
git add -A && git commit -m "Snapshot before MPR work — all current features working"
git checkout -b mpr-dev
# All MPR work happens on mpr-dev branch
# If something breaks: `git checkout main` (or `git stash`)
```

If user doesn't want git: zip the project folder before starting.

### Layer 2 — Parallel HTML file (the actual approach)

Instead of modifying `test-heroui.html` directly, create a copy and add MPR
to the copy. The original keeps working.

```bash
cp test-heroui.html test-heroui-ct.html
```

The user opens `test-heroui-ct.html` for the experimental MPR version.
`test-heroui.html` stays untouched and accessible at the original URL.

Once MPR is stable and tested, we can:
- Diff the two files and selectively merge MPR additions into the original
- Or rename `test-heroui-ct.html` → `test-heroui.html` and archive the old

**Decisions already made:**
- Modify the file: `test-heroui-ct.html` (new copy, original untouched)
- Use 1 NiiVue instance with `SLICE_TYPE.MULTIPLANAR` (renders 3 slices in 1 canvas)
- Scroll wheel + buttons for slice navigation: YES
- Crosshair-click navigation: NO (only scroll to navigate)
- Implant overlay Phase 4: start with **Option A** (mesh overlay), keep
  **Option C** (real 2D outline) documented for later

## Web-app constraints

This is a planning app that runs in browser. Therefore:
- Avoid heavy WASM modules where possible
- NIfTI compressed is 64MB — stream via `fetch`, don't load into localStorage
- NiiVue itself is ~600KB minified, loaded via CDN, OK
- Mesh-plane intersection (Option C) is JS-side, must be fast (< 50ms per slice)
- Disable MPR rendering when CT column is hidden (button off) — no background draws

## Fase 0 — Setup files (do once)

```bash
# Copy NIfTI volume into data/
cp "/Users/brunogobbato/Dropbox/CODEX/Planning App/storage/ct_cases/teste-506460eb/processing/selected_series_0000.nii.gz" \
   "data/selected_series_0000.nii.gz"

# Create the parallel HTML file
cp test-heroui.html test-heroui-ct.html
```

Add NiiVue via CDN to `test-heroui-ct.html` head:
```html
<script src="https://unpkg.com/@niivue/niivue@latest/dist/niivue.umd.js"></script>
```

## Fase 1 — UI: column + CT toggle button (30 min)

**Grid change** in `test-heroui-ct.html`:
- Current: 3 cols (left sidebar | viewer | right sidebar)
- New (CT off): 3 cols (unchanged)
- New (CT on): 4 cols (left | viewer | **ct-col 320px** | right)

**HTML to add inside main container:**
```html
<div class="ct-column" id="ct-column" style="display:none">
  <canvas id="ct-canvas"></canvas>
  <div class="ct-controls">
    <button id="btn-ct-slice-up">▲</button>
    <span id="ct-slice-info">Axial 50 · Cor 50 · Sag 50</span>
    <button id="btn-ct-slice-down">▼</button>
  </div>
</div>
```

**Topbar button:**
```html
<button id="btn-ct" class="btn btn-flat btn-sm">CT</button>
```

**CSS:**
```css
body.ct-on .ct-column { display: flex; flex-direction: column; }
body.ct-on .main-grid { grid-template-columns: 200px 1fr 320px 340px; }
.ct-column { background:#0c0c1a; padding:6px; gap:6px; }
#ct-canvas { flex:1; }
.ct-controls { display:flex; justify-content:space-between; align-items:center; }
```

**Click handler:**
```js
document.getElementById('btn-ct').addEventListener('click', () => {
  const on = document.body.classList.toggle('ct-on');
  if (on && !nv) initMPR();   // lazy init — only when first opened
  if (nv) nv.drawScene();     // force redraw on toggle
});
```

## Fase 2 — NiiVue MULTIPLANAR rendering (1-2h)

NiiVue's `SLICE_TYPE.MULTIPLANAR` shows the 3 standard views in a single
canvas, with a built-in mini 3D render in the 4th quadrant (we can hide it).

```js
let nv = null;
async function initMPR() {
  nv = new niivue.Niivue({
    sliceType: niivue.SLICE_TYPE.MULTIPLANAR,
    backColor: [0.05, 0.05, 0.1, 1],
    crosshairColor: [0, 0, 0, 0],       // hide the crosshair (decision: NO)
    show3Dcrosshair: false,
    multiplanarShowRender: niivue.SHOW_RENDER.NEVER, // disable the 3D corner
  });
  await nv.attachToCanvas(document.getElementById('ct-canvas'));
  await nv.loadVolumes([{
    url: 'data/selected_series_0000.nii.gz?v=' + Date.now(),
    colormap: 'gray',
  }]);
  console.log('[MPR] Volume loaded:', nv.volumes[0].dims);
}
```

**Slice navigation (scroll wheel):**
```js
document.getElementById('ct-canvas').addEventListener('wheel', (e) => {
  if (!nv) return;
  e.preventDefault();
  // NiiVue's setSliceMM moves crosshair which moves all 3 slices in sync
  const delta = e.deltaY > 0 ? 1 : -1;
  // figure out which quadrant the cursor is in to know which axis to scroll
  // NiiVue has nv.moveCrosshairInVox([dx, dy, dz]) — use this
  nv.moveCrosshairInVox([0, 0, delta]);  // adjust based on hovered quadrant
});
```

**Buttons just trigger the same scroll logic.**

## Fase 3 — Coordinate alignment (30 min, critical)

Verify the implant overlay will land in the right place.

**Known coordinate facts:**
- NIfTI physical mm space: `physical = origin_xyz + voxel × spacing_xyz`
- OBJ meshes (scapula/humerus) live in the same NIfTI physical mm space
- In the 3D scene (test-heroui), the scapula is RE-CENTERED via
  `scapulaMesh.position = -glenoid_center`, so the implant world position
  in the 3D scene is `glenoid_center + (whatever I2P does)`
- The NIfTI volume in NiiVue is at its ORIGINAL position (not re-centered)

**Conversion**: to map an implant point from the 3D scene back to the NIfTI
world (for the overlay), we add back the glenoid_center offset.

```js
function sceneToNifti(pointInScene) {
  return new THREE.Vector3(
    pointInScene.x + glenoid_center_xyz_mm[0],
    pointInScene.y + glenoid_center_xyz_mm[1],
    pointInScene.z + glenoid_center_xyz_mm[2],
  );
}
```

NiiVue accepts world-mm coordinates directly. No voxel conversion needed.

## Fase 4 — Implant overlay

Three options, in order of complexity. We start with **A**.

### Option A — NiiVue mesh overlay (start here, ~1h)

NiiVue can load OBJ/STL meshes and render them in the slice views. It
handles the slice-clipping automatically (shows only the part of the mesh
intersecting the slice plane region).

```js
// After volume loaded
const implantSTL = await fetch('data/glenoid_anat_2_short.stl').then(r => r.arrayBuffer());
const meshData = niivue.NVMesh.readMesh(implantSTL, 'implant.stl');
// Apply I2P transform — NiiVue needs world-mm vertices
// ... transform mesh vertices by I2P, then add glenoid_center offset
nv.addMesh({
  url: null,
  buffer: implantSTL,
  rgba255: [255, 165, 0, 200],  // orange overlay
});
```

**Pro**: Fast to implement. Looks correct enough.
**Con**: Renders as a full 3D mesh per slice, not a pure 2D outline.

### Option B — Three.js clipping plane overlay (intermediate, ~3h)

Reserved for if Option A looks bad. Render a Three.js scene on top of each
slice with two tight clipping planes (slice_position ± 0.3mm), showing only
the cross-section of the implant. More work to sync with NiiVue's crosshair.

### Option C — True 2D outline at slice plane (best, ~5-6h)

For each slice, compute the intersection of the implant mesh with the slice
plane (mesh-plane intersection algorithm → returns 2D polygon segments).
Draw those segments as an orange polyline on an HTML5 2D canvas overlay
positioned on top of each NiiVue slice region.

Algorithm sketch:
- Iterate triangles in implant geometry
- For each triangle, find edges crossing the slice plane
- Collect intersection points → assemble into a closed polygon
- Project to 2D using the slice plane's basis
- Draw polyline on overlay canvas

**Pro**: Anatomically correct outline, exactly what medical systems show.
**Con**: Requires implementing mesh-plane intersection, recompute on every
slice change.

**Implementation note for the future**: store implant geometry in a flat
Float32Array (positions only), keep at module scope, recompute outline only
when the slice changes (debounced 50ms).

## Fase 5 — Sync with implant adjustments (30 min)

When the surgeon adjusts retroversion/inclination/depth, the I2P changes.
The overlay must update.

In test-heroui-ct.html, in `updateImplantPose()`:
```js
function updateImplantPose() {
  // ... existing code ...
  if (typeof updateMPRImplantOverlay === 'function') updateMPRImplantOverlay();
}
```

Where `updateMPRImplantOverlay()`:
- Option A: removes old NiiVue mesh, recomputes vertices with new I2P, re-adds
- Option C: recomputes the 2D polygon and redraws on overlay canvas

Throttle this if it's slow — surgeon clicks adjust buttons rapidly.

## Fase 6 — Polish

- Auto-jump to `glenoid_center.xyz_mm` voxel when CT opens (slice through glenoid)
- Window/level slider (contrast)
- Toggle button: show/hide the implant overlay independently of the CT
- Persist CT-on state to localStorage so it stays toggled across reloads
- (Future) `Sync 3D` button: click in a slice → camera flies to that point

## Estimated effort

| Phase | Estimate | Cumulative |
|--|--|--|
| 0 — Setup files | 15min | 15min |
| 1 — UI/toggle | 30min | 45min |
| 2 — NiiVue render | 1-2h | 2:45 |
| 3 — Coordinates | 30min | 3:15 |
| **MVP STOP** — CT visible, navigatable, no implant overlay yet | | |
| 4A — Mesh overlay | 1h | 4:15 |
| 5 — Sync with adjusts | 30min | 4:45 |
| 6 — Polish | 1-2h | ~6h |
| (Future) 4C — Real outline | 5-6h extra | ~12h total |

## Risks & test points

1. **NIfTI file size (64MB)** — NiiVue streams it; check network tab for slow load
2. **CORS** — Python http.server is OK; Vercel may need `Access-Control-Allow-Origin: *`
3. **NiiVue + Three.js coexistence** — both use WebGL, different canvases, should be fine
4. **Coordinate alignment** — early test: place a marker at `glenoid_center.xyz_mm`,
   should appear exactly at the visual glenoid center in the CT slice
5. **Memory** — implant mesh is 100-200KB, OK. NIfTI loaded once in NiiVue, OK
6. **Performance under adjust** — clicking retroversion fast should not lag MPR;
   use 200ms debounce for the overlay re-render

## Suggested order for next session

1. ✅ Run git backup commit (Layer 1 safety)
2. ✅ Run `cp test-heroui.html test-heroui-ct.html` (Layer 2 safety)
3. ✅ Copy NIfTI to `data/`
4. ✅ Phase 1 + 2: get CT visible and scrollable in the new file
5. ⏸️ **PARAR e testar** — só ver a CT funcionando ja eh grande vitoria
6. Fase 4A: implant mesh overlay (Option A)
7. Fase 5: sync with implant adjustments
8. Fase 6: polish

After MVP works:
- Diff `test-heroui-ct.html` vs `test-heroui.html`
- Merge MPR additions into the original (or rename ct → main)
- Update dashboard to also show MPR (separate plan)

## Rollback plan if MPR breaks something

- `test-heroui.html` is never touched → just open the original URL
- `git checkout main` to discard mpr-dev branch
- Delete `data/selected_series_0000.nii.gz` to save 64MB
- Remove NiiVue script tag from any HTML file

## Files this plan will touch

| File | Action |
|--|--|
| `test-heroui-ct.html` | NEW (copy of test-heroui.html) |
| `data/selected_series_0000.nii.gz` | NEW (64MB copy) |
| `MPR_PLAN.md` | THIS PLAN |
| `CLAUDE.md` | Add a one-line pointer to this plan |
| `test-heroui.html`, `humerus.html`, `surgery-dashboard.html` | UNCHANGED |
