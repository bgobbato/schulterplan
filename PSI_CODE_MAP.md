# PSI Code Map — `test-psi.html` (~1940 linhas)

Mapa de navegação rápida do código. Pra próxima sessão Claude ou developer humano
saber EXATAMENTE onde achar cada coisa.

---

## Layout do arquivo

```
1-280     HTML structure (header, sidebars, viewer)
281-313   <style> CSS (HeroUI dark theme)
314       <script type="importmap"> — CDN URLs
326-329   <script type="module"> opens — imports
331-345   State (state object, LEG_NAMES, LEG_COLORS)
346-376   Three.js setup (renderer, scene, camera, controls, lighting)
377-394   Globals (scapulaMesh, axes, etc)
395-408   parsePipelinePayload() — payload → P2G matrix + axes
409-432   loadScapula() — OBJLoader with cache-bust
433-490   autoPlaceLegs(), snapToScapula() — initial 120° positions
473-504   createLegSpheres() — visual leg spheres + outlines
505-560   Drag interaction (pointerdown/move/up + Esc)
561-686   Visualizations (contact plane, K-wire viz, skeleton wireframe)
687-742   UI updates (coord labels, validation checks)
743-755   Persistence (saveState/loadState — v2 schema with patientId)
756-792   Camera views (glenoid/anterior/lateral/superior)
793-823   Display toggles + reset button + patient ID input
824-854   PSI constants (PSI object — sizes, segments)
855-901   computeKwireBoneEntry(), computePSIGeometry() — derived geometry
902-1066  three-bvh-csg functions (makeCylinderBrush, makeSphereBrush, makeScapulaBrush, cleanCSGGeometry)
1067-1145 manifold-3d setup (initManifoldEngine, geomToManifold, manifoldToGeom)
1146-1180 manifoldCylinder — bake-into-vertices approach
1181-1286 PATIENT ID TEXT block (PSI_TEXT, loadPSIFont, buildPatientIDTextManifold)
1287-1295 manifoldSphereAt
1296-1333 getScapulaManifold — MeshLab-cleaned mesh loader
1334-1529 ★ generatePSIManifold — MAIN GENERATION FUNCTION
1530-1555 manifoldCheck — open-edge counter
1556-1631 generatePSI — BVH engine version
1632-1687 showPSIMesh — display result + auto-hide overlays + auto-zoom
1688-1788 refreshOpenEdgeOverlay + button handlers (generate, download)
1789-1937 Init block + animate loop
```

---

## Funções-chave (quick reference)

### Geometria
| Function | Linhas | Output |
|---|---|---|
| `parsePipelinePayload(payload)` | 380 | P2G matrix from friedman/glenoid_si axes |
| `loadScapula(url)` | 413 | THREE.Group da escapula |
| `autoPlaceLegs()` | 434 | 3 Vector3 a 120° |
| `snapToScapula(point)` | 457 | Vector3 snapped na superfície |
| `computeKwireBoneEntry()` | 858 | Vector3 onde K_axis bate no osso |
| `computePSIGeometry()` | 880 | Struct {K, centralBase, centralCenter, feet[], legs[]} |

### CSG (manifold-3d) — caminho do sucesso
| Function | Linhas | Faz |
|---|---|---|
| `initManifoldEngine()` | 1086 | Carrega WASM, marca code version |
| `geomToManifold(geom, mergeTol)` | 1097 | THREE.BufferGeometry → Manifold (strip non-pos + weld) |
| `manifoldToGeom(m)` | 1130 | Manifold → THREE.BufferGeometry |
| `manifoldCylinder(...)` | 1168 | Cilindro orientado via bake-into-vertices |
| `manifoldSphereAt(...)` | 1287 | Esfera centrada via `.translate()` |
| `getScapulaManifold(offset)` | 1296 | Escapula → Manifold (com fallback tolerância) |
| `loadPSIFont()` | 1192 | Carrega helvetiker do CDN, cached |
| `buildPatientIDTextManifold(g)` | 1206 | Texto embossed → Manifold (null se vazio/falhar) |
| **`generatePSIManifold()`** | **1334** | **MAIN — pipeline completo CSG** |

### CSG (three-bvh-csg) — fallback
| Function | Linhas | Faz |
|---|---|---|
| `makeCylinderBrush(...)` | 921 | Brush orientado (THREE.CylinderGeometry) |
| `makeSphereBrush(...)` | 932 | Brush esfera |
| `makeScapulaBrush(offset)` | 1013 | Brush da escapula (cached) |
| `cleanCSGGeometry(geom)` | 946 | mergeVertices + remove degenerates |
| `generatePSI()` | 1556 | Pipeline BVH (produz open edges) |

### UI / Visualization
| Function | Linhas | Faz |
|---|---|---|
| `createLegSpheres()` | 474 | 3 esferas coloridas com outline |
| `updateContactPlane()` | 566 | Disc azul no plano dos 3 contatos |
| `updateKwireVisualization()` | 606 | Cilindro verde 120mm |
| `updateSkeleton()` | 632 | Wireframe preview do PSI |
| `updateValidation()` | 701 | 4 checks (spacing, rim, area, K-wire) |
| `setView(name)` | 760 | Câmera glenoid/anterior/lateral/superior |
| `showPSIMesh(result)` | 1632 | Adiciona PSI mesh + auto-hide + auto-zoom |
| `refreshOpenEdgeOverlay()` | 1688 | Linhas vermelhas em open edges (debug) |

---

## Estado e persistência

### `state` global object (linha 318)
```javascript
{
  planning,        // pipeline payload + parsed
  caseId,          // ex 'teste-506460eb'
  legs,            // [Vector3, Vector3, Vector3] em world coords
  draggingLeg,     // -1 ou índice 0-2
  patientId,       // string max 10 chars
}
```

### localStorage key
`schulterplan_psi_${caseId}` — schema v2:
```json
{
  "version": 2,
  "caseId": "teste-506460eb",
  "savedAt": "2026-05-31T...",
  "legs": [[x,y,z], [x,y,z], [x,y,z]],
  "patientId": "JD-2026"
}
```

### Globals derivados (linha 357)
- `scapulaMesh` — THREE.Group (re-centrado)
- `scapulaSurfaceMesh` — Mesh raycaster target
- `glenoidCenter` — Vector3 (sempre (0,0,0) após re-centering)
- `glenoidNormal` — Vector3 (superfície real da glenoide)
- `friedmanAxis` — Vector3 (K_axis, P2G col 2)
- `glenoidUp`, `glenoidRight` — Vector3 (frame da glenoide)
- `kwireBoneEntry` — Vector3 (onde K bate no osso)

### Const cache
- `_fontCache` — helvetiker JSON, cached after first load
- `_scapulaBrushCache` — BVH brush cache (per scapula geom)
- `_scapulaManifoldCache` — não usado atualmente (recomputa cada vez)
- `_scapulaPreCleanStats` — diagnose info

---

## Constants

### `PSI` (linha 829) — geometria do guia
```javascript
{
  FOOT_DIAMETER: 10, FOOT_HEIGHT: 6, FOOT_EMBED: 3,
  CENTRAL_DIAMETER: 10, CENTRAL_HEIGHT: 20, CENTRAL_OFFSET_FROM_BONE: 3,
  LEG_DIAMETER: 6, LEG_DIRECTION: 'free',
  FILLET_DIAMETER: 8,
  KWIRE_DIAMETER: 2.5, KWIRE_LENGTH: 200,
  BONE_OFFSET: 0.0,
  CYL_SEGMENTS: 96, CYL_HEIGHT_SEGMENTS: 12, SPHERE_SEGMENTS: 48,
  MERGE_TOLERANCE: 1e-2, SCAPULA_MERGE_TOLERANCE: 1e-3,
  DEGENERATE_AREA: 1e-6,
  SKIP_BONE_SUBTRACT: false,
}
```

### `PSI_TEXT` (linha 1183) — patient ID embossing
```javascript
{
  CHAR_HEIGHT: 1.8,         // mm
  EMBOSS_DEPTH: 1.2,        // total extrusion
  EMBOSS_OVERLAP: 0.4,      // sink into cylinder
  UPPER_RATIO: 0.65,        // position along K
  CURVE_BIAS: false,        // future: wrap text
}
```

### Naming
- `LEG_NAMES` = `['upper', 'middle', 'lower']`
- `LEG_COLORS` = `[0xff5470 (vermelho), 0x5fd96e (verde), 0x4fc3ff (azul)]`
- `LS_KEY(caseId)` = `'schulterplan_psi_' + caseId`

---

## Code versioning convention

Cada mudança em `generatePSIManifold` ou `manifoldCylinder` bumpa marker:
```javascript
console.log('%c[PSI] code build: vN (descrição)', 'color:#5fd96e;font-weight:bold');
console.log('%c[PSI] generatePSIManifold vN (descrição)', 'color:#ffb84d;font-weight:bold');
```

**Versions** até agora:
- v1-v5: experimentação de transform/rotate
- v6: offset=0, WASM error decoding
- v7: granular post-boolean diagnostics
- v8: always-on diagnostics + cache-busted
- **v9**: reordered K-wire 16-seg first, bone last (FIRST WORKING)
- **v10**: patient ID embossed (CURRENT)

Pra forçar fresh load: `?v=N` no URL.

---

## Debug helpers permanentes no código

| Helper | Onde | Output |
|---|---|---|
| `dumpBbox(label, manifold)` | dentro de `generatePSIManifold` | bbox + center per primitive |
| `decodeErr(err)` | dentro de `generatePSIManifold` | decodifica WASM exception ptrs |
| Per-step try/catch | bone subtract, K-wire subtract, status, getMesh | identifica passo exato |
| Final bbox check | em `showPSIMesh` | "size > 100mm = bug" warning |
| `manifoldCheck(geom)` | linha 1530 | open + non-manifold edges count |

---

## Onde adicionar X

| Quero... | Onde editar |
|---|---|
| Mudar tamanho do guia | `PSI` object linha 829 |
| Adicionar PSI template | Novo branch em `generatePSIManifold` baseado em `state.template` |
| Adicionar UI control | Sidebar HTML + event listener perto da linha 800 |
| Adicionar label embossed nos pés | Nova função baseada em `buildPatientIDTextManifold` |
| Mudar font do patient ID | `loadPSIFont` linha 1192 — CDN URL |
| Debug primitive ruim | Adicionar `dumpBbox('label', primitive)` em `generatePSIManifold` |
| Adicionar campo no localStorage | Update `saveState` + `loadState` + state object + bump version |
