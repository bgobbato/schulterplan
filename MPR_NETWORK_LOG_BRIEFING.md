# Network Log Analysis Briefing — MPR / CT Implementation

**Read this first**: you are receiving this in a fresh Claude session with no prior context. The user will share a network log (HAR file, browser DevTools network export, or similar) from a working medical planning tool that handles CT MPR rendering. Your job is to extract anything useful for replicating that capability in our own web-based shoulder planning app.

---

## What we're trying to build

A web-based shoulder arthroplasty planner where the surgeon can:
1. View the patient's CT in **3 standard slice planes** (axial, coronal, sagittal) simultaneously — classic MPR (Multi-Planar Reconstruction)
2. Navigate slices with **scroll wheel + ▲▼ buttons** (no crosshair click)
3. See the **planned glenoid implant drawn as an outline overlay** in each slice, in the exact 3D position the surgeon has positioned it

The CT volume comes from a NIfTI file (`.nii.gz`, ~64MB compressed). The implant is a 3D mesh (STL/OBJ) that has been positioned via a 4x4 transformation matrix (I2P — Implant-to-Patient).

The app is **pure browser, no build step**: vanilla JavaScript + Three.js (via importmap CDN). The MPR will use NiiVue.js (also via CDN).

## What we already have working

- Three.js 3D viewer showing the scapula mesh, humerus mesh, and implant
- Implant positioned via `I2P = P2G × adjustM × I2G` where:
  - `P2G` (Patient-to-Glenoid) is a 4×4 row-major matrix from the pipeline payload
  - `adjustM` is built from surgeon-controlled retroversion/inclination/depth/tx/ty/rotz
  - `I2G` is the implant-to-glenoid base transform (identity for pipeline cases)
- Pipeline data in `planning_payload.json` provides:
  - NIfTI volume path: `processing/selected_series_0000.nii.gz`
  - Coordinate system: `nifti_physical_xyz_mm`
  - `origin_xyz` and `spacing_xyz_mm` for voxel↔mm conversion
  - All anatomical landmarks in `xyz_mm`
- The OBJ meshes and the NIfTI volume share the SAME physical mm coordinate system (marching cubes from same NIfTI)

## What's still unknown / what we want to learn from the log

The network log presumably comes from a working medical planning system (Effigos Explorer, Implantcast GPS, Mimics, or similar). We want to learn:

### 1. CT data transport
- How does the reference system serve CT to the browser?
  - Full NIfTI download upfront? Chunked streaming?
  - Pre-rendered slice images (PNG/JPEG per slice) — server-side rendering?
  - Tiled image pyramids (like OpenSeadragon for pathology)?
  - WebGL volume textures sent as binary?
- File formats: NIfTI? DICOM? Custom binary? PNG sequence?
- Compression: gzip? Brotli? JPEG quality settings?
- Chunk sizes (any pattern like 256x256x256 sub-volumes?)
- Endpoint patterns (REST? GraphQL? WebSocket for slice streaming?)

### 2. Slice navigation / state
- When the surgeon scrolls, does the browser fetch a new slice image, or does it have the whole volume and slice client-side?
- Are slice indices sent to server (e.g. `GET /ct/axial/123`) or computed locally?
- Latency per slice change (look at timing)

### 3. Implant overlay
- Is the implant outline:
  - Sent as 2D SVG/path per slice from the server (server computes mesh-plane intersection)?
  - Sent as full 3D mesh and rendered client-side over the slice?
  - Pre-rendered into the slice image itself?
- If client-side: what library? Look for Three.js, BabylonJS, NiiVue, VTK.js, OHIF, Cornerstone3D references in the request URLs or JS files
- Mesh format if separate: STL, GLB, OBJ, custom?

### 4. Coordinate system handling
- Look for any API responses that include affine matrices, voxel-to-world transforms, or DICOM-style ImageOrientationPatient/ImagePositionPatient strings
- Look for landmark coordinates in JSON responses — what format?

### 5. Performance / architecture
- Is heavy computation (mesh-plane intersection, MPR resampling) done server-side or client-side?
- Look for WebSocket / Server-Sent Events that might indicate live streaming
- Look for Web Worker scripts (they may be loaded as separate JS bundles)
- Look for WASM (`.wasm`) downloads — sign of heavy client-side compute (Emscripten medical imaging libs)

### 6. Libraries / frameworks signals
Things to grep for in the URLs and JS file names:
- `niivue`, `cornerstone`, `ohif`, `vtk.js`, `itk-wasm`, `dwv`, `dicomweb`, `papaya`, `ami.js`
- `gl-matrix`, `three`, `babylonjs`
- Any `.wasm` files
- Any `.nrrd`, `.nii`, `.mha`, `.dcm`, `.dicomweb` in URLs

### 7. Rendering quality clues
- Window/level (contrast) — sent as URL params or in JSON?
- Interpolation mode (nearest vs trilinear) — any hints in shader code if served?
- MIP / MPR / VR (Volume Rendering) — does the log show 3 separate slice requests or one volume?

## What to report back

Please produce a structured findings report with:

1. **Architecture summary** — server-side rendering vs client-side, key technologies identified
2. **CT data delivery** — format, chunking, endpoints, sizes
3. **Implant overlay strategy** — how the reference system does it
4. **Coordinate handling** — any transforms or matrices in the responses
5. **Recommended approach for our app** — given what you found, should we still go with NiiVue + Option A (mesh overlay), or is there a better approach the reference system uses?
6. **Red flags** — anything that would NOT work in a pure-browser app without a backend (e.g. server-side rendering pipeline)

Format the report as a markdown file so we can paste it back into the main project session.

## Constraints on the recommendation

Our app:
- Is **pure browser** — no backend (Python http.server serves static files)
- Runs on **Vercel** in production (static hosting)
- Cannot ship server-side mesh-plane intersection or volume resampling
- Cannot ship anything that requires a license key or authenticated session
- Must work with NIfTI files (the pipeline outputs these — not DICOM)
- Target: surgeons reviewing a single case at a time, no need for multi-patient

Anything that requires a heavy backend is OUT for our use case, but still useful to know if the reference system relies on one — we'd just pick a different path.

## Our current plan (for context)

In `MPR_PLAN.md` (separate file) we documented:
- **Library**: NiiVue.js with `SLICE_TYPE.MULTIPLANAR` (3 slices in 1 canvas)
- **Implant overlay**: start with Option A (NiiVue mesh overlay — quick), eventually Option C (real 2D outline via mesh-plane intersection — clean but harder)
- **Safety**: implement in a parallel file `test-heroui-ct.html` to not break the working version

Your findings will help us validate or pivot this plan.

## Pipeline coordinate facts (in case useful)

From `planning_payload.json` for case `teste-506460eb`:

```json
{
  "coordinate_systems": {
    "editable_landmarks": {
      "type": "nifti_voxel_zyx",
      "units": "voxel",
      "source_volume": "processing/selected_series_0000.nii.gz"
    },
    "physical": {
      "type": "nifti_physical_xyz_mm",
      "units": "mm",
      "origin_xyz": [-47.9, -171.5, -79.55],
      "spacing_xyz_mm": [0.67, 0.67, 0.625]
    }
  }
}
```

The OBJ meshes used in our 3D view are in `nifti_physical_xyz_mm`. The implant is positioned via a 4×4 row-major matrix `patientRefToGlenoidRef` (P2G) that operates in the same mm space.

For NiiVue overlay alignment we'll need:
```js
const physical_mm = origin_xyz + voxel × spacing_xyz
```

NiiVue accepts world-mm directly for `addMesh` calls (no manual voxel conversion needed).

---

**End of briefing**. Please ask for the network log file from the user, analyze it, and produce the findings report described in "What to report back".
