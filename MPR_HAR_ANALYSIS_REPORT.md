# HAR Analysis Report — CustomedAI (app.customed.ai) MPR Implementation

**Source**: `app.customed.aiDATA.har` — 43 HTTP entries captured from a shoulder arthroplasty planning session on `app.customed.ai` (case 40-30, left shoulder RSA).

**Date of analysis**: 2026-05-29

---

## 1. Architecture Summary

### The system: CustomedAI — a cloud-based shoulder planning platform

| Layer | Technology |
|---|---|
| **Frontend** | React SPA (Vite bundled), Three.js for 3D |
| **Volume engine** | **"Medusa"** — proprietary WebGL2 volume renderer (v0.2.64) |
| **DICOM parsing** | Custom client-side parser using `dcmjs` (`DicomMessage.readFile`) + **OpenJPEG WASM** for JPEG2000 decompression |
| **3D library** | Three.js (bundled, not via CDN) |
| **Mesh format** | STL inside ZIP archives (segmented anatomies + landmarks) |
| **CT delivery** | DICOM ZIP from S3/CloudFront CDN → client unzips + parses → 3D texture |
| **Contour overlay** | **Client-side mesh-to-slice contour** via render-target multi-pass |
| **Additional libs** | Cornerstone3D (event types referenced but Medusa does the volume rendering), VTK.js (clipping planes shader code) |
| **Auth** | JWT-based sessions, S3 pre-signed URLs for file access |
| **Error tracking** | Sentry |
| **Analytics** | Intercom |

### Key architectural insight
**Everything is client-side.** The server is essentially a file store (S3 + CloudFront) with a thin REST API for case metadata and pre-signed URL generation. All heavy lifting — DICOM parsing, volume construction, MPR slicing, mesh contour rendering — happens in the browser.

---

## 2. CT Data Delivery

### Format: Raw DICOM files inside a ZIP archive

The case metadata contains:
```json
"dicomFileUri": "s3://prod-customedai-storage/cases/40/RSA/40-30/dicoms/ct_1778678060760/dcm.zip"
```

### Download flow
1. Client POSTs to `/api/fileUpload/{orgId}/download` with the S3 path
2. Server returns a **CloudFront pre-signed URL** + byte range info
3. Client fetches the ZIP from `prod-cdn.customed.ai` (CloudFront)
4. **No DICOM download appears in this HAR capture** — likely cached from a previous session or the recording started after the download

### Volume construction (from console logs)
```
DICOM load success {
  attempt: 1,
  fileCount: 276,        // 276 DICOM slices
  blobSizeMb: 62.24,     // ~62MB uncompressed ZIP
  downloadMs: 80,        // 80ms (cached/pre-loaded)
  downloadThroughputMbps: 6223.75
}
```

### Client-side DICOM parsing pipeline
From the JS bundles, the parsing chain is:

1. **Unzip** — JSZip extracts `.dcm` files from the ZIP
2. **Filter** — skip non-DICOM files (`.txt`, `.json`, `.xml`, etc.)
3. **Parse each slice** — `DicomMessage.readFile()` from `dcmjs` library:
   - Extracts: `ImagePositionPatient`, `ImageOrientationPatient`, `PixelSpacing`, `SliceThickness`, `Rows`, `Columns`, `RescaleSlope/Intercept`, `WindowCenter/Width`
   - Handles JPEG2000 transfer syntax via **OpenJPEG WASM** (`openjpegwasm_decode-B3gWTHpv.wasm`)
   - Supports 8-bit and 16-bit pixel data (signed/unsigned)
4. **Sort slices** by `ImagePositionPatient` z-position
5. **Build volume** — `Lb()` function constructs:
   - `pixelData`: typed array (Int16/Uint16)
   - `dimensions`: `[cols, rows, depth]` (276 slices)
   - `spacing`: `[pixelSpacing[0], pixelSpacing[1], sliceSpacing]`
   - `origin`: from first slice `ImagePositionPatient`
   - `direction`: 3×3 from `ImageOrientationPatient` (9 elements)
   - `rescaleSlope`, `rescaleIntercept`
   - `initialWindowLevel`: from DICOM tags
6. **Upload to GPU** — volume data → WebGL2 `sampler3D` texture (normalized to Uint8)

### Chunking strategy
**None** — the entire DICOM series is downloaded as a single ZIP, parsed client-side, and loaded into one 3D texture. No streaming, no tiling, no progressive loading.

### WASM dependency
`openjpegwasm_decode-B3gWTHpv.wasm` — for JPEG2000 compressed DICOM. Standard CT is usually uncompressed or JPEG lossless, so this may not fire for all cases.

---

## 3. Implant / Mesh Overlay Strategy

### How CustomedAI draws mesh contours on 2D CT slices

This is the most valuable finding. They use a **multi-pass WebGL rendering approach**:

#### Step 1: Mesh Contour Render Target
The Medusa `VolumeEngine` maintains per-viewport **render targets** (`meshSliceContourRTs`) where the 3D meshes are rasterized from the same camera angle as the 2D slice view:

```javascript
this.meshSliceContourRTs = new Map();        // per viewport
this.meshSliceContourBlurRTs = new Map();    // blur pass
this.contourMeshes = [];                     // 3D meshes to contour
this.contourThickness = 5.5;                 // pixels
this.contourSuperSampling = 2;               // anti-aliasing factor
this.contourColor = new Color(0x8AB8F8);     // blue-ish
```

Properties:
- `contour2DWidth: 10` — contour line width
- `fillContour2D: false` — outline only (can be filled)
- `fillContour2DOpacity: 0.8`
- `subtleContour2DFillOpacity: 0.5`
- `showContourOnly2D: false` — whether to hide CT and show only contour
- `contourSuperSampling2D: 4` — 4x supersampling for anti-aliased contour edges

Each mesh can have:
- `contour2DType` — type of contour rendering
- `contour2DFillAlpha` — per-mesh fill opacity
- `contour2DColorOverride` — per-mesh color override

#### Step 2: Slice Plane with Contour Texture
Each MPR viewport has a **`slicePlane`** — a Three.js plane mesh positioned at the volume center. Its shader material samples TWO textures:

1. **`volumeTexture`** (sampler3D) — the full CT volume
2. **`meshSliceContourTex`** (sampler2D) — the mesh contour render target

#### Step 3: Fragment Shader Compositing
The slice plane fragment shader:
1. Samples the 3D volume at `vTextureCoord` → applies window/level → grayscale or LUT color
2. Projects `vLocalPosition` through `modelViewMatrix` + `projectionMatrix` to get screen UV
3. Samples `meshSliceContourTex` at that screen UV
4. **Blends** contour over CT using screen-blend + contrast enhancement:

```glsl
// Blend contour over CT
float contourAlpha = meshSliceContour.a * contourFillOpacity2D * 1.35;
vec3 contourColor = meshSliceContour.rgb;
vec3 screenedContour = screenBlend(volumeCol, contourColor);
vec3 contrastContour = mix(screenedContour, contourColor, 0.72);
// Boost dark/bright contours differently
float dominance = smoothstep(0.02, 0.95, contourAlpha) * 0.92;
volumeCol = mix(volumeCol, boostedContour, dominance);
```

#### Step 4: Cache + Invalidation
Contour render targets are cached per viewport and invalidated when:
- Camera changes (projection or world-inverse matrix)
- Meshes change (add/remove/transform)
- `invalidateContourCache(viewportId)` is called explicitly

A cooldown period (`CONTOUR_COOLDOWN_MS`) prevents thrashing during rapid interaction.

### Key insight for our implementation
**They do NOT compute mesh-plane intersections.** Instead, they render the 3D meshes from the same orthographic camera as the CT slice, capture to a render target, and composite the result. This is much simpler than computing geometric intersections — it's just standard GPU rasterization with a multi-pass blend.

---

## 4. Coordinate System Handling

### Anatomical axis matrices (4×4 row-major)
The API returns per-anatomy 4×4 transforms in the landmark data:

```json
"anatomicalAxis": {
  "humerus_left": [
    [0.127, -0.966, -0.225, -259.929],
    [0.964,  0.068,  0.256,  240.038],
    [-0.232, -0.249,  0.940, 1173.300],
    [0, 0, 0, 1]
  ],
  "scapula_left": [
    [-0.497, -0.809, -0.314, -330.033],
    [ 0.866, -0.481, -0.132, -149.748],
    [-0.044, -0.338,  0.940, 1164.399],
    [0, 0, 0, 1]
  ]
}
```

These are world-space transforms (DICOM patient coordinate space). The translation column gives the anatomy center position in mm.

### DICOM → Volume transform
The volume engine constructs the voxel-to-world transform from:
- `ImagePositionPatient` (3 floats) → volume origin
- `ImageOrientationPatient` (6 floats) → direction cosines (3×3 matrix)
- `PixelSpacing` (2 floats) + slice spacing → voxel dimensions
- `direction` matrix (9 elements, column-major) stored in volume data

The shader uses this via:
```javascript
const dirMat = new Matrix4();
dirMat.set(
  direction[0], direction[3], direction[6], 0,
  direction[1], direction[4], direction[7], 0,
  direction[2], direction[5], direction[8], 0,
  0, 0, 0, 1
);
```

### Volume properties (from console)
```
dimensions: [cols, rows, 276]
spacing: [pixelSpacing[0], pixelSpacing[1], sliceSpacing]
origin: [x, y, z]  // ImagePositionPatient of first slice
```

---

## 5. Mesh / Anatomy Delivery

### Segmentation meshes: STL files in ZIP
- `anatomies_4.zip` (6.7 MB) — contains bone meshes as STL:
  - `anatomies_4/MAIN#humerus_left.stl`
  - `anatomies_4/MAIN#scapula_left.stl`

### Landmarks: STL planes + point spheres in ZIP
- `landmarks.zip` (2.5 MB) — contains:
  - `landmarks/scapula_left#POINT#Glenoid Center_modifier_skippedSphere_dont_export`
  - `landmarks/scapula_left#POINT#Trigonum Scapulae_modifier_skippedSphere_dont_export`
  - `landmarks/scapula_left#POINT#Inferior Angle Of The Scapula_...`
  - `landmarks/scapula_left#POINT#Supraspinous Fossa-Glenoid Intersection_...`
  - `landmarks/scapula_left#POINT#Supraspinous Fossa-Medial Intersection_...`
  - `landmarks/scapula_left#PLANE#Glenoid Plane.stl`
  - `landmarks/humerus_left#POINT#Medial Epicondyle Tip_...`
  - `landmarks/humerus_left#POINT#Greater Tuberosity Lateral_...`
  - `landmarks/humerus_left#POINT#Lesser Tuberosity Lateral_...`
  - `landmarks/humerus_left#POINT#Proximal Anatomical_...`
  - `landmarks/humerus_left#POINT#Distal Anatomical_...`
  - `landmarks/humerus_left#PLANE#Humeral Neck Plane.stl`

### Mesh loading
Uses GLTFLoader and custom STL parser. Meshes support:
- Visibility toggling per mesh (`ContourVisibility` logging)
- Per-mesh contour color/opacity
- Auto-alignment between meshes (overlap detection)

---

## 6. Volume Rendering Engine ("Medusa")

### Architecture
Medusa is a custom WebGL2 volume renderer with these key features:

| Feature | Implementation |
|---|---|
| Volume rendering | Ray-marching fragment shader (stepSize=0.01, maxSteps=256) |
| MPR slicing | 3 orthographic viewports: CT_AXIAL, CT_CORONAL, CT_SAGITTAL |
| Window/level | Per-viewport via `updateWindowLevel(viewId, centerDelta, widthDelta)` |
| Mesh contour on slice | Render-target rasterization + shader compositing |
| Slice indicators | Cross-reference lines showing other slice positions |
| Clipping planes | Per-axis clipping (axial/sagittal/coronal) with direction control |
| Brightness/Contrast/Gamma | Shader uniforms: brightness=0.09, contrast=1.12, gamma=0.98 |
| LUT colormaps | Hot Iron, Cool, Grayscale + custom presets |
| Supersampling | 2-4x for contour anti-aliasing |

### Slice navigation
- `updateSlice(viewId, normalizedPosition)` — positions 0.0–1.0 within volume
- `getNumSlices(viewId)` — returns total slices for that orientation
- All client-side — no server calls for navigation

### Volume rendering shader (key uniforms)
```glsl
uniform sampler3D volumeTex;          // Full CT volume as 3D texture
uniform float stepSize;                // Ray march step (0.01)
uniform float maxSteps;                // Max ray steps (256)
uniform float windowCenter;            // HU center
uniform float windowWidth;             // HU window width
uniform float rescaleSlope;            // DICOM rescale
uniform float rescaleIntercept;        // DICOM intercept
uniform float axialSliceZ;             // Slice indicator positions
uniform float sagittalSliceX;
uniform float coronalSliceY;
uniform float showSliceIndicators;     // Toggle crosshairs
uniform float enableClipAxial;         // Clipping plane toggles
uniform float enableClipSagittal;
uniform float enableClipCoronal;
```

---

## 7. Performance Characteristics

| Metric | Value |
|---|---|
| Main JS bundle | 2.9 MB (`index-DkSmr2Kk.js`) |
| Three.js editor bundle | 1.3 MB (`ThreejsEditor-BZ-BwQjl.js`) |
| Cornerstone/VTK bundle | 1.0 MB (`ZoomTool-Baxo3Z2V.js`) |
| DICOM dictionary | 1.2 MB (`isEqual-CjeuRf6k.js` — includes full DICOM tag dict) |
| Anatomies ZIP | 6.7 MB (2 bone STLs) |
| Landmarks ZIP | 2.5 MB (planes + points as STL) |
| DICOM ZIP | ~62 MB (276 slices) |
| **Total initial load** | **~75 MB** |
| DICOM parse time | Not captured (likely 5-15s) |
| WASM dependency | OpenJPEG decoder (~100KB .wasm) |

---

## 8. Red Flags — What Won't Work Without a Backend

| Requirement | CustomedAI approach | Impact for us |
|---|---|---|
| **DICOM serving** | S3 pre-signed URLs via authenticated API | We serve NIfTI from static files — no issue |
| **Auth/access** | JWT + org-based access control | N/A for single-user local app |
| **DICOM parsing** | Client-side dcmjs + OpenJPEG WASM | We use NIfTI — NiiVue handles this natively |
| **Segmentation** | Server-side AI pipeline | We already have pipeline output |
| **Medusa engine** | Proprietary, not available | Must use NiiVue or build custom |

### Critical: Medusa is proprietary
The "Medusa" volume engine is CustomedAI's proprietary renderer. It is NOT an open-source library — it's compiled into their bundle. We cannot extract or use it.

However, the **architecture** is fully replicable:
- Volume → 3D texture → fragment shader slicing = standard approach
- Mesh contour via render-target rasterization = standard Three.js technique

---

## 9. Recommended Approach for Our App

### Verdict: Keep NiiVue plan, but adopt Medusa's contour strategy

Based on this analysis, our MPR_PLAN.md approach is **validated with one major upgrade**:

### Volume Rendering: NiiVue ✅ (keep as planned)
NiiVue does everything Medusa does for volume rendering:
- Loads NIfTI directly (we skip DICOM parsing entirely)
- Provides axial/coronal/sagittal MPR views
- Has window/level, LUT colormaps, slice navigation
- Is open-source and MIT-licensed

### Implant Overlay: Adopt Medusa's render-target approach 🔄 (pivot from Option A)

**Instead of** NiiVue's built-in mesh overlay (Option A in MPR_PLAN.md), consider Medusa's approach:

| Approach | Pros | Cons |
|---|---|---|
| **Option A: NiiVue mesh overlay** | Quick to implement, built-in | Limited control, may not look great |
| **Option C: Geometric intersection** | Precise outlines | Complex math, CPU-intensive |
| **Option D: Medusa-style render target** (NEW) | Clean contours, standard WebGL, GPU-accelerated | Need separate Three.js renderer per viewport |

**Option D workflow:**
1. NiiVue renders the CT slice to its canvas
2. A separate Three.js scene renders the implant mesh from the same orthographic camera + same slice plane → to a WebGL render target
3. Composite the contour texture over the NiiVue canvas (either via CSS overlay or canvas-2D drawImage)

This is **architecturally clean** because:
- NiiVue handles all volume rendering (its strength)
- Three.js handles mesh rendering (our existing strength)
- No mesh-plane intersection math needed
- Contour quality is GPU-native (anti-aliased, configurable thickness)
- Synchronization = just match the camera/slice position between NiiVue and Three.js

### Phased implementation

| Phase | What | Effort |
|---|---|---|
| **Phase 1** | NiiVue MPR with 3 slice views, scroll navigation, window/level | 1-2 days |
| **Phase 2** | Option A (NiiVue addMesh) for quick implant overlay | 0.5 day |
| **Phase 3** | Option D (render-target contour) for production-quality overlay | 2-3 days |
| **Phase 4** | Slice indicators (cross-reference lines between views) | 1 day |

### Why NOT to use Cornerstone3D
CustomedAI bundles Cornerstone3D (~1MB) but appears to use it only for events/enums, not for actual rendering. Medusa does all the work. This confirms that for a focused shoulder planner, a lighter approach (NiiVue or custom) beats the full OHIF/Cornerstone stack.

---

## 10. Specific Technical Takeaways

### For NiiVue integration
- NiiVue loads NIfTI directly — skip the entire DICOM parsing pipeline CustomedAI needs
- Volume dimensions, spacing, and origin come from NIfTI header automatically
- NiiVue's `SLICE_TYPE.MULTIPLANAR` gives us 3 views in one canvas

### For contour rendering
- CustomedAI uses **4x supersampling** for contour quality — worth doing
- Contour thickness of **5.5 pixels** (device-independent) looks good on screen
- The **screen-blend + contrast enhancement** compositing shader makes contours visible on both bright and dark CT regions
- Per-viewport **contour caching** with camera-change invalidation is essential for performance

### For coordinate alignment
- CustomedAI's anatomical axis matrices are in the same space as the DICOM patient coordinate system
- Our pipeline's `nifti_physical_xyz_mm` is equivalent — the affine in the NIfTI header maps voxels to this space
- **The key alignment step**: when rendering the contour, the Three.js camera must match NiiVue's orthographic projection for that slice exactly

### Window/level defaults
- CustomedAI defaults: brightness=0.09, contrast=1.12, gamma=0.98
- These are post-windowing display adjustments, not the window/level itself
- Window/level comes from DICOM tags (WindowCenter, WindowWidth)

---

## Appendix: Network Request Inventory

| # | URL Pattern | Size | Purpose |
|---|---|---|---|
| 0 | `/40-30/editor?...` | 643B | SPA HTML shell |
| 1 | `index-DkSmr2Kk.js` | 2.9MB | Main React bundle |
| 9 | `/api/case/by-case-number/40-30` | 6KB | Case metadata (dicomFileUri, segmentations, anatomicalAxis) |
| 13 | `ThreejsEditor-BZ-BwQjl.js` | 1.3MB | Three.js + Medusa volume engine + shaders |
| 17 | `isEqual-CjeuRf6k.js` | 1.2MB | DICOM tag dictionary (dcmjs) |
| 19 | `ViewerTools-C4UL6aad.js` | 104KB | loadDicomForVolume, window/level tools |
| 20 | `ZoomTool-Baxo3Z2V.js` | 1.0MB | Cornerstone3D + VTK.js (clipping, events) |
| 25 | `/api/tasks/prepareforcases` | - | Trigger server-side compute |
| 28 | `/api/segmentation/latest/6342` | 534B | Segmentation metadata (zip path, series) |
| 29 | `/api/landmark/latest/6342` | 1KB | Landmark data + anatomicalAxis matrices |
| 34 | `/api/fileUpload/40/download` | 604B | Get pre-signed URL for anatomies ZIP |
| 35 | `anatomies_4.zip` | 6.7MB | Bone STL meshes (humerus + scapula) |
| 37 | `/api/fileUpload/40/download` | 596B | Get pre-signed URL for landmarks ZIP |
| 38 | `landmarks.zip` | 2.5MB | Landmark STLs (planes + points) |
| 41 | `PreAnatomies-CX0km-YR.js` | 66KB | Pre-anatomy viewer (Medusa instance #2) |

**Notable absence**: The DICOM ZIP download (~62MB) is NOT in this HAR — likely cached from a previous session or the recording started after the download completed.
