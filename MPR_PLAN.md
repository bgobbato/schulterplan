# MPR (CT) Implementation Plan — Multi-Planar Reconstruction v2

**Status**: Approved — ready to implement
**Last updated**: 2026-05-29
**Target file**: `test-heroui-ct.html` (new copy, original untouched)
**Reference analysis**: `MPR_HAR_ANALYSIS_REPORT.md` (CustomedAI HAR analysis)

---

## Context — What this session needs to know

This is a web-based shoulder arthroplasty planner. The app is pure browser
(vanilla JS + Three.js via importmap CDN, no build step). It runs on Vercel
as static files.

We analyzed a competing platform (CustomedAI / app.customed.ai) via HAR network
log capture. Their system uses a proprietary WebGL2 volume renderer called
"Medusa" with client-side DICOM parsing. We can't use their code, but we
extracted their architecture patterns — especially their implant contour overlay
strategy (render-target rasterization, not mesh-plane intersection).

### Key architectural differences from CustomedAI

| Aspect | CustomedAI | Our app |
|---|---|---|
| CT format | DICOM ZIP (276 .dcm files, ~62MB) | NIfTI `.nii.gz` (~64MB) |
| Volume engine | "Medusa" (proprietary WebGL2) | NiiVue.js (MIT, via CDN) |
| DICOM parsing | dcmjs + OpenJPEG WASM (~3MB JS) | None needed — NiiVue reads NIfTI natively |
| 3D engine | Three.js (bundled) | Three.js (via importmap CDN) |
| Build system | Vite + React (~6MB bundles) | None — single HTML files |
| Contour overlay | Render-target rasterization (Option D) | Start Option A, migrate to Option D |
| Auth/backend | JWT + S3 pre-signed URLs | Static files, no auth |

### What CustomedAI does well (adopt these patterns)

1. **Contour overlay via render target** — rasterize mesh from slice camera → texture → composite over CT
2. **Slice indicators** (crosshair lines) — colored lines showing other slice positions
3. **Floating toolbar** — 3 icons: Pan (hand), Zoom (magnifier), W/L (half-circle)
4. **Landmark planes** — glenoid plane and neck plane as visible semi-transparent meshes
5. **Per-viewport contour cache** with camera-change invalidation
6. **4x supersampling** for anti-aliased contour edges

---

## Goal

Add a CT column to the scapula planner showing 3 MPR slices (axial, coronal,
sagittal) with the planned implant visible as a contour overlay. The surgeon
scrolls through slices to verify implant position relative to bone anatomy.

## Safety strategy

### Layer 1 — Git branch
```bash
cd "/Users/brunogobbato/Dropbox/Claude Workspace/Advita/gps-web-planner Implantcast"
git checkout -b mpr-experiment
git add -A && git commit -m "Snapshot before MPR work — all current features working"
git checkout -b mpr-dev
```

### Layer 2 — Parallel file
```bash
cp test-heroui.html test-heroui-ct.html
```
All MPR work goes in `test-heroui-ct.html`. Original is NEVER modified.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│  test-heroui-ct.html                                                │
│                                                                      │
│  ┌─────────┐  ┌──────────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ Left    │  │  3D Viewer       │  │  CT Column   │  │ Right    │ │
│  │ Sidebar │  │  (Three.js)      │  │  (NiiVue)    │  │ Sidebar  │ │
│  │         │  │                  │  │              │  │          │ │
│  │ Implant │  │  Scapula mesh    │  │ ┌──────────┐ │  │ Adjust   │ │
│  │ Select  │  │  + Implant       │  │ │  Axial   │ │  │ Controls │ │
│  │         │  │  + Landmarks     │  │ │  ──────  │ │  │          │ │
│  │         │  │                  │  │ │ Coronal  │ │  │          │ │
│  │         │  │                  │  │ │  ──────  │ │  │          │ │
│  │         │  │                  │  │ │ Sagittal │ │  │          │ │
│  │         │  │                  │  │ └──────────┘ │  │          │ │
│  │         │  │                  │  │  [🤚][🔍][◐] │  │          │ │
│  └─────────┘  └──────────────────┘  └──────────────┘  └──────────┘ │
│                                                                      │
│  Topbar: ... [CT] ...                                                │
└──────────────────────────────────────────────────────────────────────┘
```

### Two WebGL contexts (independent)
- **Canvas 1**: Three.js — existing 3D viewer (scapula, implant, orbit controls)
- **Canvas 2**: NiiVue — CT volume (axial/coronal/sagittal MPR)
- **Canvas 3** (Phase 7): Three.js render target — implant contour for overlay on CT

They share coordinate data but not WebGL state.

### Coordinate alignment
Both Three.js meshes and NIfTI volume live in `nifti_physical_xyz_mm` space.
In the 3D viewer, the scapula is re-centered: `scapulaMesh.position = -glenoidCenter`.
To map from 3D scene → NIfTI world: add glenoidCenter back.

```js
function sceneToNifti(scenePoint) {
  return new THREE.Vector3().copy(scenePoint).add(glenoidCenter_xyz_mm);
}
```

NiiVue uses world-mm directly — no voxel conversion needed for overlay.

---

## Implementation Phases

### Phase 0 — Setup (15 min)

**Files to create/copy:**
```bash
# NIfTI volume → data/
cp "/Users/brunogobbato/Dropbox/CODEX/Planning App/storage/ct_cases/teste-506460eb/processing/selected_series_0000.nii.gz" \
   "data/selected_series_0000.nii.gz"

# Parallel HTML file
cp test-heroui.html test-heroui-ct.html
```

**Add NiiVue to `test-heroui-ct.html` importmap:**
```html
<script src="https://unpkg.com/@niivue/niivue@latest/dist/niivue.umd.js"></script>
```

**Verify NIfTI file exists and size:**
```bash
ls -lh data/selected_series_0000.nii.gz
# Should be ~64MB
```

---

### Phase 1 — CT Column UI + Toggle (30 min)

**Grid layout change:**
- CT off: `200px 1fr 340px` (unchanged)
- CT on: `200px 1fr 400px 340px`

Column is 400px wide (not 320px as originally planned — wider gives better
diagnostic quality per slice, confirmed by CustomedAI's generous viewport sizing).

**HTML to add** (inside main container, between viewer and right sidebar):
```html
<div class="ct-column" id="ct-column">
  <div class="ct-header">
    <span class="ct-title">CT MPR</span>
    <div class="ct-toolbar" id="ct-toolbar">
      <button class="ct-tool active" data-tool="scroll" title="Scroll slices">
        <svg><!-- scroll/crosshair icon --></svg>
      </button>
      <button class="ct-tool" data-tool="pan" title="Pan">
        <svg><!-- hand icon --></svg>
      </button>
      <button class="ct-tool" data-tool="zoom" title="Zoom">
        <svg><!-- magnifier+ icon --></svg>
      </button>
      <button class="ct-tool" data-tool="wl" title="Window/Level">
        <svg><!-- half-circle icon --></svg>
      </button>
    </div>
  </div>
  <canvas id="ct-canvas"></canvas>
  <div class="ct-info" id="ct-info">
    <span id="ct-slice-label">Slice: —</span>
    <span id="ct-wl-label">W/L: —</span>
  </div>
</div>
```

**Topbar button:**
```html
<button id="btn-ct" class="btn btn-flat btn-sm">CT</button>
```

**CSS:**
```css
.ct-column {
  display: none;
  flex-direction: column;
  background: #0a0a1a;
  border-left: 1px solid #2a2a3a;
  min-width: 400px;
}
body.ct-on .ct-column { display: flex; }
body.ct-on .main-grid { grid-template-columns: 200px 1fr 400px 340px; }

.ct-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 6px 10px; border-bottom: 1px solid #2a2a3a;
}
.ct-title { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #888; }

.ct-toolbar {
  display: flex; gap: 4px; background: #1a1a2e; border-radius: 8px; padding: 3px;
}
.ct-tool {
  width: 32px; height: 32px; border: none; background: transparent;
  border-radius: 6px; cursor: pointer; color: #aaa;
  display: flex; align-items: center; justify-content: center;
}
.ct-tool.active { background: #2563eb; color: white; }
.ct-tool:hover:not(.active) { background: #2a2a3a; }

#ct-canvas { flex: 1; min-height: 0; }

.ct-info {
  display: flex; justify-content: space-between; padding: 4px 10px;
  font-size: 11px; color: #666; border-top: 1px solid #2a2a3a;
}
```

**Toggle handler:**
```js
document.getElementById('btn-ct').addEventListener('click', () => {
  const on = document.body.classList.toggle('ct-on');
  document.getElementById('btn-ct').classList.toggle('active', on);
  if (on && !state.nv) initMPR();
  if (!on && state.nv) state.nv.drawScene(); // keep state but stop drawing
  // Resize existing Three.js viewer (it now has less space)
  window.dispatchEvent(new Event('resize'));
});
```

---

### Phase 2 — NiiVue Volume Rendering (1-2h)

**Initialize NiiVue with MULTIPLANAR layout:**
```js
let nv = null;

async function initMPR() {
  nv = new niivue.Niivue({
    sliceType: niivue.SLICE_TYPE.MULTIPLANAR,
    backColor: [0.05, 0.05, 0.1, 1],

    // Crosshairs ON (changed from original plan — essential for orientation)
    crosshairColor: [0.2, 0.8, 0.2, 0.5],  // green, semi-transparent
    crosshairWidth: 1,
    show3Dcrosshair: false,

    // Hide 4th quadrant (3D render) — save GPU
    multiplanarShowRender: niivue.SHOW_RENDER.NEVER,

    // Drag behavior per mouse button
    dragMode: niivue.DRAG_MODE.none,  // we handle tools via toolbar
  });

  await nv.attachToCanvas(document.getElementById('ct-canvas'));

  await nv.loadVolumes([{
    url: 'data/selected_series_0000.nii.gz?v=' + Date.now(),
    colormap: 'gray',
  }]);

  state.nv = nv;
  console.log('[MPR] Volume loaded:', nv.volumes[0].dims);

  // Jump to glenoid center on first load
  if (state.planning && state.planning._pipelinePayload) {
    const gc = state.planning._pipelinePayload.landmarks.scapula.glenoid_center.xyz_mm;
    nv.scene.crosshairPos = nv.mm2frac([gc[0], gc[1], gc[2]]);
    nv.drawScene();
  }

  setupCTToolbar();
  updateCTInfo();
}
```

**Scroll navigation (per-quadrant):**
```js
document.getElementById('ct-canvas').addEventListener('wheel', (e) => {
  if (!nv) return;
  e.preventDefault();
  const delta = e.deltaY > 0 ? 1 : -1;

  // Determine which quadrant the cursor is over
  const rect = e.target.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width;
  const y = (e.clientY - rect.top) / rect.height;

  // NiiVue MULTIPLANAR layout: axial=top-left, coronal=top-right, sagittal=bottom-left
  let axis;
  if (x < 0.5 && y < 0.5) axis = [0, 0, delta];       // axial → scroll Z
  else if (x >= 0.5 && y < 0.5) axis = [0, delta, 0];  // coronal → scroll Y
  else if (x < 0.5 && y >= 0.5) axis = [delta, 0, 0];  // sagittal → scroll X
  else return; // 4th quadrant (hidden)

  nv.moveCrosshairInVox(axis);
  updateCTInfo();
});
```

**Toolbar tool switching:**
```js
function setupCTToolbar() {
  const tools = document.querySelectorAll('.ct-tool');
  tools.forEach(btn => {
    btn.addEventListener('click', () => {
      tools.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tool = btn.dataset.tool;
      switch (tool) {
        case 'scroll': nv.opts.dragMode = nv.dragModes.none; break;
        case 'pan':    nv.opts.dragMode = nv.dragModes.pan; break;
        case 'zoom':   nv.opts.dragMode = nv.dragModes.zoom; break;
        case 'wl':     nv.opts.dragMode = nv.dragModes.contrast; break;
      }
    });
  });
}
```

**CT info bar update:**
```js
function updateCTInfo() {
  if (!nv || !nv.volumes[0]) return;
  const pos = nv.frac2mm(nv.scene.crosshairPos);
  document.getElementById('ct-slice-label').textContent =
    `X:${pos[0].toFixed(1)} Y:${pos[1].toFixed(1)} Z:${pos[2].toFixed(1)} mm`;
  const vol = nv.volumes[0];
  document.getElementById('ct-wl-label').textContent =
    `W:${vol.cal_max - vol.cal_min} L:${((vol.cal_max + vol.cal_min) / 2).toFixed(0)}`;
}
```

**Test point**: At this point CT should be visible and navigatable. STOP and verify:
- 3 slices visible (axial, coronal, sagittal)
- Scroll wheel changes slices per quadrant
- Green crosshairs visible
- Toolbar tools work (pan, zoom, W/L)
- No interference with existing Three.js viewer

---

### Phase 3 — Coordinate Alignment Verification (30 min)

Before adding the implant overlay, verify coordinates match.

**Test**: Place a NiiVue marker at glenoid_center and check it lands
at the visual center of the glenoid in the CT slices.

```js
// In console after CT loads:
const gc = state.planning._pipelinePayload.landmarks.scapula.glenoid_center.xyz_mm;
console.log('[MPR] Glenoid center mm:', gc);
const frac = nv.mm2frac([gc[0], gc[1], gc[2]]);
console.log('[MPR] Glenoid center frac:', frac);
nv.scene.crosshairPos = frac;
nv.drawScene();
// The crosshair should be exactly at the glenoid center in all 3 views
```

If it's off, check:
1. NIfTI header qform/sform vs our `origin_xyz` and `spacing_xyz_mm`
2. Axis ordering (NiiVue uses RAS by default, our pipeline uses... check)
3. Off-by-one in origin (NIfTI origin is corner vs center of first voxel)

---

### Phase 4 — Implant Overlay: Option A (MVP, 1h)

Start with NiiVue's built-in mesh rendering. Quick to implement,
validates coordinate alignment, may be "good enough".

```js
async function addImplantToMPR() {
  if (!nv || !state.implantMesh) return;

  // Get implant geometry vertices in scene space
  const geom = state.implantMesh.geometry;
  const positions = geom.attributes.position.array.slice(); // copy

  // Transform vertices: scene → NIfTI world
  // Scene has scapula re-centered, so add glenoidCenter back
  // Also apply the implant's world matrix (I2P transform)
  const implantMatrix = state.implantMesh.matrixWorld;
  const gc = state.planning.glenoidCenter; // THREE.Vector3

  const tempV = new THREE.Vector3();
  for (let i = 0; i < positions.length; i += 3) {
    tempV.set(positions[i], positions[i+1], positions[i+2]);
    tempV.applyMatrix4(implantMatrix);  // local → scene world
    tempV.add(gc);                       // scene → NIfTI world
    positions[i] = tempV.x;
    positions[i+1] = tempV.y;
    positions[i+2] = tempV.z;
  }

  // Build a minimal mesh buffer for NiiVue
  // NiiVue addMesh expects specific format — check API
  // Alternative: create a temporary STL/OBJ in memory

  // If NiiVue mesh overlay looks bad, skip to Phase 7 (Option D)
}
```

**Evaluation criteria for Option A:**
- Does the implant appear in the right position?
- Is the outline visible and distinct from bone?
- Does it update when surgeon adjusts retroversion/inclination?
- If ANY of these fail or look poor → skip to Phase 7

---

### Phase 5 — Sync Overlay with Implant Adjustments (30 min)

When the surgeon clicks retroversion/inclination/depth buttons in the right
sidebar, the implant moves in the 3D viewer. The MPR overlay must follow.

Hook into `updateImplantPose()`:
```js
function updateImplantPose() {
  // ... existing I2P matrix computation ...
  // ... existing mesh position update ...

  // Update MPR overlay (debounced)
  if (state.nv && document.body.classList.contains('ct-on')) {
    scheduleMPROverlayUpdate();
  }
}

let _mprUpdateTimer = null;
function scheduleMPROverlayUpdate() {
  clearTimeout(_mprUpdateTimer);
  _mprUpdateTimer = setTimeout(() => {
    updateMPRImplantOverlay();  // Option A: rebuild mesh, Option D: invalidate render target
  }, 200);
}
```

---

### Phase 6 — Polish (1-2h)

**6a. Auto-jump to glenoid on CT open:**
Already in Phase 2 init code.

**6b. Brightness/Contrast via CSS filter:**
```js
function setCTDisplayCurve(brightness, contrast) {
  const canvas = document.getElementById('ct-canvas');
  canvas.style.filter = `brightness(${brightness}) contrast(${contrast})`;
}
// Default values from CustomedAI analysis:
setCTDisplayCurve(1.09, 1.12);
```

**6c. Persist CT state to localStorage:**
```js
const CT_STATE_KEY = (caseId) => `schulterplan_ct_${caseId}`;
// Save: { ctOn: bool, crosshairPos: [x,y,z], calMin, calMax }
// Restore on init
```

**6d. Implant overlay toggle (independent of CT):**
Add checkbox in ct-header: "Show implant" — toggles overlay visibility
without closing CT.

**6e. Slice number display:**
Show current slice index (e.g., "Axial 142/276") in the info bar.

---

### Phase 7 — Implant Contour: Option D (2-3h)

**This is the production-quality overlay**, adopted from CustomedAI's architecture.
Only implement after Option A is working and coordinates are verified.

**Architecture:**
```
NiiVue canvas (CT slices)
        ↓ composited via CSS overlay
Contour canvas (Three.js render targets → 2D canvas)
```

**Step 1: Create a second Three.js renderer (offscreen)**
```js
const contourRenderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
contourRenderer.setSize(400 * 2, canvasHeight * 2); // 2x supersampling
contourRenderer.setClearColor(0x000000, 0);          // transparent background

const contourScene = new THREE.Scene();
const contourTarget = new THREE.WebGLRenderTarget(
  400 * 2, canvasHeight * 2,
  { format: THREE.RGBAFormat, type: THREE.UnsignedByteType }
);
```

**Step 2: Add implant mesh clone to contour scene**
```js
const contourImplantMesh = state.implantMesh.clone();
contourImplantMesh.material = new THREE.MeshBasicMaterial({
  color: 0x8AB8F8,   // CustomedAI's contour blue
  wireframe: false,
  side: THREE.DoubleSide,
});
// Position in NIfTI world space (NOT re-centered)
// Apply I2P + glenoidCenter offset
contourScene.add(contourImplantMesh);
```

**Step 3: For each slice view, render from matching orthographic camera**
```js
function renderContourForSlice(sliceType, slicePosition_mm) {
  // Create orthographic camera matching NiiVue's view
  const cam = new THREE.OrthographicCamera(
    -viewHalfWidth, viewHalfWidth,
    viewHalfHeight, -viewHalfHeight,
    -500, 500
  );

  // Position camera to match slice orientation
  switch (sliceType) {
    case 'axial':
      cam.position.set(slicePosition_mm[0], slicePosition_mm[1], slicePosition_mm[2] + 100);
      cam.lookAt(slicePosition_mm[0], slicePosition_mm[1], slicePosition_mm[2]);
      cam.up.set(0, 1, 0);
      break;
    case 'coronal':
      cam.position.set(slicePosition_mm[0], slicePosition_mm[1] + 100, slicePosition_mm[2]);
      cam.lookAt(slicePosition_mm[0], slicePosition_mm[1], slicePosition_mm[2]);
      cam.up.set(0, 0, 1);
      break;
    case 'sagittal':
      cam.position.set(slicePosition_mm[0] + 100, slicePosition_mm[1], slicePosition_mm[2]);
      cam.lookAt(slicePosition_mm[0], slicePosition_mm[1], slicePosition_mm[2]);
      cam.up.set(0, 0, 1);
      break;
  }

  // Render to offscreen target
  contourRenderer.setRenderTarget(contourTarget);
  contourRenderer.render(contourScene, cam);
  contourRenderer.setRenderTarget(null);

  // Read pixels and draw on overlay canvas
  // (or use the render target texture directly)
}
```

**Step 4: Composite on overlay canvas**
```html
<canvas id="ct-contour-overlay"
  style="position:absolute; top:0; left:0; pointer-events:none; z-index:10;">
</canvas>
```
```js
function compositeContour() {
  const overlay = document.getElementById('ct-contour-overlay');
  const ctx = overlay.getContext('2d');
  ctx.clearRect(0, 0, overlay.width, overlay.height);

  // For each quadrant, draw the contour render target
  // Map NiiVue's quadrant layout to our render target regions
  // ...
}
```

**Step 5: Cache + invalidation**
```js
const contourCache = new Map(); // viewType → { cameraHash, imageData }

function invalidateContourCache(viewType) {
  contourCache.delete(viewType);
}

// Invalidate on:
// - Slice scroll (crosshair position changed)
// - Implant adjustment (I2P changed)
// - Implant selection changed
// - Window resize
```

**Key sync challenge:**
The contour camera must EXACTLY match NiiVue's internal camera for each quadrant.
NiiVue doesn't expose its camera matrices directly, so we need to:
1. Get crosshair position via `nv.scene.crosshairPos` → `nv.frac2mm()`
2. Get zoom level via `nv.scene.volScaleMultiplier` or similar
3. Get viewport layout (which quadrant is where) from NiiVue's canvas dimensions
4. Reconstruct the orthographic projection to match

This is the trickiest part. If NiiVue's API doesn't expose enough camera info,
fallback to Option B (Three.js clipping planes on a transparent canvas overlay).

---

### Phase 8 — Landmark Planes (30 min)

Add visible semi-transparent planes for anatomical reference.

**Glenoid Plane:**
```js
function addLandmarkPlanes() {
  const payload = state.planning._pipelinePayload;
  const glenoidPlane = payload.planes.glenoid_plane;

  // Plane geometry in NIfTI world space
  const planeGeom = new THREE.PlaneGeometry(60, 60);
  const planeMat = new THREE.MeshBasicMaterial({
    color: 0x00ff88,
    transparent: true,
    opacity: 0.25,
    side: THREE.DoubleSide,
    depthTest: true,
  });
  const planeMesh = new THREE.Mesh(planeGeom, planeMat);

  // Position at glenoid center (in scene space = minus glenoidCenter offset)
  const point = glenoidPlane.point_xyz_mm || glenoidPlane.center_xyz_mm;
  planeMesh.position.set(
    point[0] - glenoidCenter.x,
    point[1] - glenoidCenter.y,
    point[2] - glenoidCenter.z
  );

  // Orient by normal
  const normal = new THREE.Vector3(...glenoidPlane.normal_xyz);
  planeMesh.lookAt(planeMesh.position.clone().add(normal));

  scene.add(planeMesh);
  state.landmarkPlanes = state.landmarkPlanes || [];
  state.landmarkPlanes.push(planeMesh);

  // Also add to contour scene for CT overlay (Phase 7)
}
```

**Toggle:** Add "Planes" checkbox in left sidebar or topbar.

---

## Estimated Effort (Revised)

| Phase | Description | Estimate | Cumulative |
|---|---|---|---|
| 0 | Setup files | 15 min | 15 min |
| 1 | CT column UI + toggle + toolbar | 45 min | 1h |
| 2 | NiiVue volume rendering + scroll + tools | 1.5h | 2:30 |
| 3 | Coordinate alignment verification | 30 min | 3:00 |
| **MVP 1** | **CT visible, navigatable, crosshairs, toolbar** | | **3:00** |
| 4 | Implant overlay Option A (NiiVue mesh) | 1h | 4:00 |
| 5 | Sync overlay with implant adjustments | 30 min | 4:30 |
| 6 | Polish (brightness, persist, info bar) | 1h | 5:30 |
| **MVP 2** | **Implant visible on CT, adjustable** | | **5:30** |
| 7 | Option D contour (render target) | 2-3h | 8:00 |
| 8 | Landmark planes | 30 min | 8:30 |
| **PRODUCTION** | **Full MPR with clean contours + planes** | | **8:30** |

## Session Execution Order

```
1. Git branch safety (Phase 0)
2. Copy files (Phase 0)
3. Phase 1 + 2: UI + NiiVue → CT visible and scrollable
4. ⏸️ PARAR e testar — CT funcionando é MVP 1
5. Phase 3: verify coordinates (crosshair at glenoid center)
6. Phase 4: implant overlay Option A
7. Phase 5: sync with adjustments
8. ⏸️ PARAR e avaliar — Option A é suficiente? Se sim, pular Phase 7
9. Phase 6: polish
10. Phase 7: Option D (only if Option A isn't clean enough)
11. Phase 8: landmark planes
```

## Risks & Mitigations

| Risk | Probability | Mitigation |
|---|---|---|
| NIfTI 64MB slow to load | Medium | NiiVue streams progressively. Show loading bar. Consider hosting on CDN for Vercel. |
| NiiVue + Three.js WebGL conflict | Low | Different canvases. Test on target laptop. |
| Coordinate misalignment | Medium | Phase 3 explicit test. Check NIfTI qform vs sform. |
| Option A looks bad (blob, not outline) | High | Skip directly to Option D. Option A is just a quick test. |
| Option D camera sync with NiiVue | Medium | If NiiVue doesn't expose camera, fallback to Option B (clipping planes). |
| Memory on surgeon's laptop | Low | NIfTI ~64MB + meshes ~1MB + textures ~5MB = ~70MB total. Fine for any modern laptop. |
| CORS on Vercel | Low | NIfTI served from same domain. No CORS issue. |

## Rollback

- `test-heroui.html` is NEVER touched → always available
- `git checkout main` discards all MPR work
- Delete `data/selected_series_0000.nii.gz` to save 64MB
- Remove NiiVue script tag from HTML

## Files This Plan Touches

| File | Action |
|---|---|
| `test-heroui-ct.html` | NEW (copy + MPR additions) |
| `data/selected_series_0000.nii.gz` | NEW (64MB NIfTI volume) |
| `MPR_PLAN.md` | THIS PLAN (updated v2) |
| `MPR_HAR_ANALYSIS_REPORT.md` | Reference (CustomedAI analysis) |
| `test-heroui.html` | **UNCHANGED** |
| `humerus.html` | **UNCHANGED** |
| `surgery-dashboard.html` | **UNCHANGED** |

## Key Reference: CustomedAI Contour Shader (for Phase 7)

The compositing shader blends contour over CT:
```glsl
// Sample mesh contour texture at screen UV
vec4 meshSliceContour = texture(meshSliceContourTex, screenUV);
float contourAlpha = meshSliceContour.a * contourFillOpacity * 1.35;

// Screen-blend for visibility on both dark and bright CT regions
vec3 screenedContour = 1.0 - (1.0 - volumeCol) * (1.0 - contourColor);
vec3 contrastContour = mix(screenedContour, contourColor, 0.72);

// Apply with dominance curve
float dominance = smoothstep(0.02, 0.95, contourAlpha) * 0.92;
volumeCol = mix(volumeCol, boostedContour, dominance);
```

CustomedAI contour defaults:
- Color: `#8AB8F8` (blue)
- Thickness: 5.5px (device-independent)
- Supersampling: 4x
- Fill: off (outline only)
- Cache cooldown: configurable per viewport
