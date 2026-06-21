# PSI Implementation — Complete Reference

**Status: ✅ FUNCIONAL com manifold-3d (31/maio/2026)**
**Arquivo: `test-psi.html` (~1940 linhas, vanilla JS + Three.js + manifold-3d WASM)**

**Última feature: Patient ID embossed (31/maio/2026)** — texto em relevo na parte superior do cilindro central, ao longo do K-axis, max 10 caracteres, facing lateral side.

## TL;DR — Receita final que funciona

```
SCAPULA → MeshLab pre-process → manifold-3d WASM CSG:
  1. Build 10 primitives (1 central + 3 feet + 3 legs + 3 fillet spheres)
  2. batchBoolean('add') union → ~5k tris
  3. Subtract K-wire FIRST (16 segs, Ø2.5mm)
  4. Subtract scapula LAST (offset=0, MeshLab-cleaned)
  5. getMesh() → 13k tris, manifold ✓
```

**Tempo: ~3s. Resultado: 0 open edges, 0 non-manifold edges.**

---

## 1. Arquitetura

### Geometria do guia (constants em `PSI`)
```
FOOT_DIAMETER: 10     // Ø10mm × 6mm — base de apoio em cada P
FOOT_HEIGHT: 6
FOOT_EMBED: 3         // metade do foot fica embebida no osso
CENTRAL_DIAMETER: 10  // Ø10mm × 20mm — cilindro central que carrega o K-wire
CENTRAL_HEIGHT: 20
CENTRAL_OFFSET_FROM_BONE: 3  // central começa 3mm acima do bone-entry do K-wire
LEG_DIAMETER: 6       // Ø6mm conectando footTop → centralCenter
LEG_DIRECTION: 'free' // direção calculada por geometria
FILLET_DIAMETER: 8    // esfera Ø8 no foot↔leg junction (smooth blend)
KWIRE_DIAMETER: 2.5   // furo de K-wire Ø2.5
KWIRE_LENGTH: 200     // 200mm garante perfurar o guia inteiro
BONE_OFFSET: 0.0      // press-fit. adicionar clearance no slicer.
CYL_SEGMENTS: 96      // primitivos do guia
CYL_HEIGHT_SEGMENTS: 12
SPHERE_SEGMENTS: 48
```

### Coordenadas
- Escapula re-centrada via `Group.position = -rawCenter` → `glenoidCenter=(0,0,0)`
- `friedmanAxis` = P2G column 2 (eixo K do K-wire)
- Pipeline xyz_mm em NIfTI physical mm (LPS)
- Implant world frame após re-center: glenoide na origem, K-wire ao longo de friedmanAxis

### Patient ID (texto embossed) — adicionado 31/maio/2026
Input field `<input id="patient-id-input" maxlength="10">` na sidebar esquerda.
Persistência em `localStorage` junto com legs (versão 2 do schema).

Parâmetros (`PSI_TEXT`):
- `CHAR_HEIGHT: 1.8` — tamanho do glifo (mm)
- `EMBOSS_DEPTH: 1.2` — extrusão total
- `EMBOSS_OVERLAP: 0.4` — afundamento na superfície do cilindro (0.4mm)
- Relevo real = 1.2 - 0.4 = **0.8mm acima da superfície**
- `UPPER_RATIO: 0.65` — posição vertical no central (0.5=meio, 1.0=topo)
- Font: `helvetiker_regular.typeface.json` da Three.js (CDN), cacheado

Orientação:
- `readDir` (texto +X) → K (eixo do cilindro)
- `upDir` (texto +Y) → tangent ao redor do cilindro
- `outDir` (texto +Z) → radial outward, projetado de `glenoidRight`

Geração:
- `buildPatientIDTextManifold(g)` retorna manifold ou null (fallback gracioso)
- Texto incluído como 11ª primitiva no `batchBoolean('add')`
- 10 chars em helvetiker ≈ 13mm de largura — cabe nos 20mm do CENTRAL_HEIGHT
- Chars com hole interno (O/D/B/P/etc) tratados pela TextGeometry via Shape+Hole; convertem OK pra manifold

Limitações conhecidas:
- Texto fica em superfície **plana tangente** (não curvado ao redor do cilindro). Deviation máx ~0.3mm em Ø10mm — visualmente aceitável.
- Para texto wrapped/curved no futuro, ver TODO em `PSI_NOTES.md` (low priority).

### 3 legs draggable
- Esferas Ø2 com outline wireframe
- Drag com `raycaster.intersectObject(scapulaMesh)` → snap automático à superfície
- Persist em `localStorage` key `schulterplan_psi_${caseId}`
- Auto-place inicial: 3 ângulos a 120° (-90°, 30°, 150°) no glenoid plane, raio 14mm, snapped

### Computed geometry (`computePSIGeometry()`)
- K = friedmanAxis (normalizado)
- kwireBoneEntry = raycast do K_axis na escapula (origem ~1mm do center)
- centralBase = kwireBoneEntry + K * 3
- centralCenter = centralBase + K * 10
- feet[i].footTop = P + K * (FOOT_HEIGHT - FOOT_EMBED) = P + K * 3
- feet[i].footCenter = midpoint(footTop, footBase)
- legs[i].dir = (centralCenter - footTop).normalize()
- legs[i].length = |centralCenter - footTop|  // tipicamente 14-22mm

---

## 2. Pipeline CSG (ordem CRÍTICA)

```javascript
async function generatePSIManifold() {
  // 1. Build 10 primitives via manifoldCylinder/manifoldSphereAt
  //    (cada um já posicionado e orientado via THREE.Matrix4 baked nos vertices)
  const central = manifoldCylinder({radius:5, height:20, axis:K, center:centralCenter});
  const feet[3] = manifoldCylinder({radius:5, height:6, axis:K, center:f.footCenter});
  const legs[3] = manifoldCylinder({radius:3, height:leg.length, axis:leg.dir, center:leg.center});
  const fillets[3] = manifoldSphereAt({radius:4, center:f.footTop});

  // 2. UNION com batchBoolean (mais rápido + mais limpo que .add() chained)
  const M = manifoldEngine.Manifold;
  let psi = M.batchBoolean([central, ...feet, ...legs, ...fillets], 'add');

  // 3. ★ ORDEM IMPORTA: K-wire ANTES do osso (descoberto após muitos erros)
  //    K-wire com SÓ 16 segments — fino + radial baixo = arestas ~0.5mm matching osso
  const kwire = manifoldCylinder({
    radius:1.25, height:200, axis:K, center:glenoidCenter,
    segments: 16, heightSegments: 24,
  });
  psi = psi.subtract(kwire);

  // 4. Bone subtract LAST (operação complexa, no resultado já com furo K-wire)
  const scapulaM = await getScapulaManifold(0);  // offset=0 evita self-intersections
  const finalPsi = psi.subtract(scapulaM);

  // 5. Convert pra THREE.js geometry
  const geom = manifoldToGeom(finalPsi);
  return { geometry: geom };
}
```

---

## 3. Pré-processamento da escapula (MeshLab manual)

A escapula vem do marching cubes (`data/scapula.obj`, ~238k tris). Mesmo "limpa", a serialização OBJ não-indexada produz vertex drift e o `mergeVertices` da Three.js não consegue weldar perfeitamente.

**Workflow MeshLab uma vez por caso:**

1. Abre `data/scapula.obj`
2. Filters → Cleaning → **Remove Duplicate Vertices**
3. Filters → Cleaning → **Remove Zero Area Faces**
4. Filters → Cleaning → **Repair non Manifold Edges**
5. Filters → Cleaning → **Remove Unreferenced Vertices**
6. Filters → Cleaning → **Repair non Manifold Vertices by splitting**
7. Filters → Remeshing → **Close Holes**
8. Filters → Smoothing → **Laplacian Smooth** (1 iteração)
9. File → Export Mesh As… → **`data/scapula_manifold.obj`**

**O loader tenta `data/scapula_manifold.obj` primeiro, com fallback pro original.**

Resultado típico após MeshLab:
- Mesmo número de tris (~238k) e verts (~119k)
- mas SEM duplicação no arquivo OBJ
- `mergeVertices(0.05mm)` reduz a 119k de uma → manifold-3d aceita

**Para automatizar futuramente:** `pymeshlab` (Python binding do MeshLab) com a chain acima.

---

## 4. JORNADA DE ERROS (a parte mais valiosa)

### Bug #1 — `Manifold.rotate([euler])` desalinhava cilindros
**Sintoma:** Tripod saía completamente torto, K-wire não furava nada visível.

**Causa:** `setFromQuaternion(q, 'XYZ').toArray() → manifold.rotate([deg,deg,deg])` —
manifold-3d v2.5.1 usa rotation order DIFERENTE de THREE.Euler 'XYZ'. Os ângulos viravam coisas erradas.

**Tentativa 1 (errada):** Trocar pra `manifold.transform(mat3x4)` com matriz column-major.

### Bug #2 — `transform(mat3x4)` ignora translation
**Sintoma:** Bbox dos primitivos centrados em (0,0,0) em vez do `center` informado, com tamanhos absurdos (200mm).

**Diagnóstico:** Adicionei `dumpBbox` per-primitiva. Cilindros saíram TODOS no origem com forma deformada (12×208×191mm pra um cilindro de 20mm). Algum bug interno do v2.5.1 com a layout de Mat3x4.

**Tentativa 2 (errada também):** Reescrever pra usar manifold-3d API diferente. Não havia uma boa.

**Tentativa 3 (CERTA):** Bake the transform into the THREE.js geometry vertices BEFORE passando pra manifold:
```javascript
const geom = new THREE.CylinderGeometry(r, r, h, segs);
geom.applyMatrix4(transformMatrix);  // baked into positions
return geomToManifold(geom);
```
Manifold só vê uma mesh "já transformada", sem precisar de rotation/translation APIs.

### Bug #3 — `mergeVertices` deixa rim aberto na cilindro
**Sintoma:** `ManifoldError: Not manifold` na criação do primeiro primitivo.

**Causa:** `THREE.CylinderGeometry` tem vertices na borda do topo/fundo com **normais diferentes** (radial nas laterais, axial nas tampas). `mergeVertices` do BufferGeometryUtils compara TODOS os attributes — não solda quando normals divergem → rim fica com aresta aberta → não-manifold.

**Fix:** Strip TODOS os attributes exceto `position` antes do `mergeVertices`:
```javascript
const stripped = new THREE.BufferGeometry();
stripped.setAttribute('position', geom.attributes.position);
if (geom.index) stripped.setIndex(geom.index);
const welded = mergeVertices(stripped, 1e-4);
```

### Bug #4 — Escapula raw não é "manifold-strict"
**Sintoma:** `Not manifold` na subtração óssea, mesmo com cilindros OK.

**Causa:** OBJ do marching cubes tem cada triângulo armazenado com seus próprios 3 vertices (não indexado), gerando vertex drift. `mergeVertices` da Three.js precisa de tolerância > 0.5mm pra consolidar, e nesse ponto vertices em FACES OPOSTAS de paredes finas se fundem → topologia destruída.

**Fix:** Pré-processar no MeshLab uma vez (workflow acima) → arquivo OBJ devidamente indexado → `mergeVertices(0.05)` recupera 119k verts perfeitos → manifold aceita.

### Bug #5 — Self-intersections com BONE_OFFSET=0.5
**Sintoma:** Após pré-processo + cilindros OK, subtração óssea passou com `✓ Bone subtraction OK` mas explodiu depois.

**Causa:** Offsetting cada vertex ao longo da normal por 0.5mm CRIA SELF-INTERSECTIONS em regiões côncavas (cavidade glenoidal) onde curvature radius < offset. A mesh offsetada vira inválida.

**Fix:** `BONE_OFFSET=0.0` (press-fit). Clearance pra impressão se adiciona no slicer ou via radial inflate dos foot cylinders (ajuste futuro).

### Bug #6 (FINAL) — Lazy evaluation explode em `status()`/`getMesh()`
**Sintoma:** Tudo funciona até o ponto:
```
✓ Bone subtraction OK
✓ K-wire subtraction OK
✗ status() threw: wasm exception ptr=536280
✗ getMesh() failed: wasm exception ptr=1060632
```

**Causa:** manifold-3d usa **lazy evaluation** — `subtract()` retorna sucesso instantâneo, mas o cálculo CSG real só acontece quando você consulta o resultado (`status`, `getMesh`). Os erros nessas funções revelam que o resultado tem **slivers degenerados** invisíveis nas operações booleanas em si.

**Subcausa específica:** K-wire Ø2.5 com **96 segments** = arestas radiais de **0.08mm**. Escapula tem arestas ~0.6mm. Quando o K-wire fino corta a superfície já bone-conformada (após bone subtract), as interseções viram slivers nanométricos que estouram tolerâncias internas do manifold.

**Fix final (DUPLO):**
1. **K-wire com 16 segments** (em vez de 96) → arestas radiais ~0.5mm = match com osso
2. **Reordenar: K-wire ANTES do osso** → operação simples no resultado limpo do union (sem detalhe da bone concavity ainda)

```javascript
psi = batchBoolean(parts, 'add');                            // clean union
psi = psi.subtract(kwire_16seg);                             // simple subtract
psi = psi.subtract(scapula);                                 // complex subtract last
```

Após isso: **✓ getMesh() OK · 13k tris · openEdges:0 · manifold ✓**.

---

## 5. Tentativas de three-bvh-csg (rejeitadas mas funcionais com repair)

three-bvh-csg subtrai a escapula sem reclamar, MAS produz:
- Triangle count maior
- **~14k open edges** (T-junctions nas interseções)
- Não-manifold → não-imprimível direto

**Workaround validado pelo user:** subir o STL pro <https://www.formware.co/onlinestlrepair> que aplica close-holes + repair e devolve manifold limpo.

Caminhos futuros pra "manifoldizar" client-side se quisermos:
1. **Close-holes JS local** — detectar loops de open edges, fan-triangulation no centroide. ~1 dia.
2. **Voxelize + marching cubes** — converte BVH result em voxels (perda de ~0.5mm res) → MC garante manifold. ~2 dias.
3. **Backend pymeshlab** — endpoint que recebe geom e devolve STL limpo. Caminho do CustomedAI. ~1-2 dias.

---

## 6. Logs/Versioning convention adotada

Cada vez que tocamos `generatePSIManifold` ou `manifoldCylinder`, bumpamos o marker:
```javascript
console.log('%c[PSI] code build: v9 (reordered: K-wire 16-seg first, bone last)',
  'color:#5fd96e;font-weight:bold');
console.log('%c[PSI] generatePSIManifold v9', 'color:#ffb84d;font-weight:bold');
```

Permite confirmar que o browser NÃO tá pegando cache stale (verificamos várias vezes).
Para forçar fresh load: `?v=9` no URL.

### Diagnostics que ficam no código permanentemente:
- Per-primitive bbox dump (`dumpBbox`) — pega bugs de orientação/translação
- Per-step try/catch com `decodeErr(err)` — decodifica WASM exception pointers
- `numProp`-aware bbox reading (manifold pode retornar mesh com normals = numProp 6)
- Final bbox check com expected range (30-45mm)

---

## 7. Arquivos relevantes

| Path | Conteúdo |
|---|---|
| `test-psi.html` | Implementação completa (~1940 lines) |
| `data/scapula.obj` | Marching cubes raw, ~238k tris |
| `data/scapula_manifold.obj` | **MeshLab-cleaned, USADO pelo manifold engine** |
| `data/planning_payload.json` | Pipeline data com landmarks + axes |
| `PSI_IMPLEMENTATION.md` | Este arquivo — reference técnico |
| `PSI_USER_GUIDE.md` | Guia cirúrgico passo-a-passo (não-técnico) |
| `PSI_CODE_MAP.md` | Mapa de navegação do test-psi.html por função/linha |
| `PSI_TROUBLESHOOTING.md` | FAQ — sintomas → fix |
| `PSI_NOTES.md` | Ideias paradas (A-H) |
| `PSI_HAR_ANALYSIS_REPORT.md` | Engenharia reversa do CustomedAI |
| `MESHLAB_PSI_WORKFLOW.md` | Passo-a-passo do MeshLab |

---

## 7b. Diagrama de arquitetura ASCII

```
┌─────────────────────────────────────────────────────────────────────┐
│ PIPELINE (upstream)                                                 │
│   CT → segmentação → marching cubes → planning_payload.json         │
│                                       data/scapula.obj              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼ (uma vez por caso)
┌─────────────────────────────────────────────────────────────────────┐
│ MESHLAB pre-process (manual ou pymeshlab)                           │
│   Remove dup verts → Remove zero area → Repair non-manifold         │
│   → Close holes → Laplacian smooth → Export                         │
│                                                                     │
│ Output: data/scapula_manifold.obj                                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ test-psi.html INIT                                                  │
│   Load payload + scapula → re-center → extract axes                 │
│   Auto-place 3 legs a 120° → restore from localStorage if exists    │
│   Preload manifold-3d WASM + helvetiker font                        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼ (user drag spheres + types patient ID)
┌─────────────────────────────────────────────────────────────────────┐
│ generatePSIManifold()                                               │
│                                                                     │
│   computePSIGeometry() → struct {K, centralCenter, feet[], legs[]}  │
│                                                                     │
│   Build 11 manifold primitives:                                     │
│     • 1 central cylinder (Ø10×20, axis K)                           │
│     • 3 foot cylinders (Ø10×6 each, axis K)                         │
│     • 3 leg cylinders (Ø6, axis foot→central, len ~15mm)            │
│     • 3 fillet spheres (Ø8 at footTop)                              │
│     • 1 patient ID text (embossed, optional)                        │
│                                                                     │
│   batchBoolean('add') ──► clean union (~5k tris)                    │
│                                                                     │
│   psi.subtract(K-wire 16-seg) ──► hole (~6k tris)  ★ K-WIRE FIRST   │
│                                                                     │
│   psi.subtract(scapula) ──► bone concavity (~13k tris)              │
│                                                                     │
│   manifoldToGeom(finalPsi) ──► THREE.BufferGeometry                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Display + Download                                                  │
│   showPSIMesh() → opaque mesh in scene + auto-zoom + auto-hide      │
│   STLExporter → binary STL ArrayBuffer → Blob download              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼ (downstream)
┌─────────────────────────────────────────────────────────────────────┐
│ SLICER → 3D PRINT → STERILIZE → SURGERY                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7c. Glossário

| Termo | Significado |
|---|---|
| **PSI** | Patient-Specific Instrument — guia 3D-impresso personalizado pro paciente |
| **Tripod** | Configuração com 3 pés de apoio (a que usamos) |
| **Glenoide** | Cavidade articular da escapula que articula com cabeça do úmero |
| **Friedman axis** | Eixo de referência clínico — perpendicular ao plano glenoidal (Friedman et al 1992). Define 0° de retroversão. |
| **K-wire** | Fio de Kirschner — pino metálico fino usado pra estabilizar/guiar |
| **Retroversão** | Ângulo de rotação posterior do plano glenoidal vs eixo de Friedman |
| **Rim** | Borda óssea da glenoide (articular margin) |
| **Marching cubes** | Algoritmo que extrai superfície de mesh a partir de volume voxel |
| **Manifold mesh** | Mesh topologicamente válida — cada aresta em exatamente 2 triângulos |
| **CSG** | Constructive Solid Geometry — operações booleanas (union/subtract/intersect) em meshes |
| **Open edge** | Aresta presente em 1 só triângulo → buraco na mesh → não-imprimível direto |
| **T-junction** | Vertex topologicamente "incompleto" em meio de uma aresta — gera open edge |
| **Embossed** | Em relevo (raised). Subtractive = engraved (sunken) |
| **2-manifold** | Topologia onde cada vertex tem vizinhança homeomorfa a um disco |
| **Helvetiker** | Font geométrica padrão do Three.js (TextGeometry) |
| **Sliver** | Triângulo degenerado, quase-zero área — comum em CSG de mismatch resolution |
| **Lazy evaluation** | Resultado de op não calculado até ser consultado (manifold-3d faz isso) |

---

## 7d. Changelog

### v12 (21/junho/2026) — K-wire segue tx/ty/depth do implant plan [BGO-154]
- Bug v11: rotação ok, mas translação tx/ty/depth do `state.adjust` era ignorada → K-wire no glenoid center mesmo com implante deslocado
- Fix: novo `kwireOrigin` separado de `glenoidCenter`
  - `kwireOrigin = glenoidCenter + tx·right + ty·up + depth·friedman`
  - Usado em `computeKwireBoneEntry`, K-wire visual e K-wire CSG subtract (BVH + manifold)
- Sidebar K-wire info mostra retro/incl/tx/ty/depth quando há ajuste

### v11 (21/junho/2026) — Integração test-heroui ↔ test-psi [BGO-154]
- Botão "Generate PSI" no topbar do test-heroui
- test-psi.html importa `caseStore.js`, carrega caso ativo (zip importado) com fallback fetch
- Lê `localStorage['schulterplan_implant_${caseId}']` e aplica `state.adjust.retroversion`/`inclination` no `friedmanAxis`
- Matemática equivalente ao `buildAdjustMatrix` do test-heroui (Euler XYZ glenoid frame)
- Botão "← Back to Planner" em destaque no header do PSI
- HUD mostra fonte (imported zip vs demo vs cleaned obj)

### v10 (31/maio/2026) — Patient ID embossed
- Added `buildPatientIDTextManifold` — texto em relevo no central cylinder
- New PSI_TEXT constants
- UI: campo input max 10 chars, persistência v2 schema
- TextGeometry + helvetiker via CDN (cached)
- Posição: upper 65% do central, facing `glenoidRight`

### v9 (31/maio/2026) — Primeira versão funcional ✅
- Reorder: K-wire FIRST (16 segs), bone LAST
- Fix: lazy-eval explodindo em `status()`/`getMesh()` por slivers
- Output: 13k tris, manifold ✓, 0 open edges

### v8 (31/maio/2026) — Diagnostics permanentes
- `decodeErr()` pra WASM exception pointers
- Per-step try/catch granular
- `dumpBbox` per-primitive
- Sempre rodam (não só debug)

### v7 (31/maio/2026) — Tentativa de mais diagnostics post-boolean
- Try/catch ao redor de `status()` e `getMesh()`
- Confirmou erro 536280 vinha do `getMesh()` (lazy eval)

### v6 (31/maio/2026) — BONE_OFFSET=0 + WASM error decoding
- Removeu self-intersections do offset
- Adicionou helper de decode de exception pointer

### v5 (31/maio/2026) — High-resolution primitives
- CYL_SEGMENTS 64→96
- CYL_HEIGHT_SEGMENTS 1→12
- SPHERE_SEGMENTS 32→48

### v4 (31/maio/2026) — Position-only weld
- Strip non-position attrs antes do mergeVertices
- Resolveu "rim aberto" do CylinderGeometry

### v3 (31/maio/2026) — numProp-aware dumpBbox
- Suporte a manifold meshes com normals embutidas
- Não usado no flow normal (sempre numProp=3 nas primitivas)

### v2 (31/maio/2026) — bake-into-vertices
- Trocou `transform(mat3x4)` por `geom.applyMatrix4` no THREE
- Resolveu "centro=0,0,0 + size=200mm" bug
- Resolveu bug de translation perdida

### v1 (30/maio/2026) — primeira tentativa manifold-3d
- `manifold.rotate([euler])` quebrado (Tait-Bryan mismatch)
- `manifold.transform(mat3x4)` ignora translation
- Tripod saía completamente torto

### pre-v1 (30/maio/2026) — three-bvh-csg
- Funciona shape-wise mas produz 14k open edges
- Validado workaround com formware.co repair

---

## 8. Próximos passos sugeridos

### Curto prazo (validação clínica)
- [ ] Baixar STL e testar no MeshMixer / slicer
- [ ] Imprimir 1 protótipo, validar fit na escapula real (cadáver ou phantom)
- [ ] Ajustar BONE_OFFSET ou adicionar radial inflate dos foot cylinders pro clearance

### Médio prazo (UX)
- [ ] Botão "Apply MeshLab workflow" que detecta `scapula_manifold.obj` ausente e abre instruções
- [ ] Salvar/restaurar perfis de geometria (ajustar diâmetros, alturas) por caso
- [ ] Modo "advanced" com sliders pros PSI params

### Longo prazo (automação backend)
- [ ] Servidor Python com `pymeshlab` — chain MeshLab no servidor, retorna scapula_manifold.obj
- [ ] Geração CSG no servidor (mais robusto, mais memória) — manifold-3d npm package
- [ ] Pipeline queue (Celery/BullMQ) + polling, igual ao CustomedAI
- [ ] PSI templates (Tripod, Tripod With Sleeve, etc) configuráveis sem código

### Long shot
- [ ] Auto-suggest leg positions baseado em densidade óssea (CT)
- [ ] Sleeve retrátil pro K-wire
- [ ] Geração para humerus (Minimal, Union templates)

---

## 9. Lições críticas pra próxima vez

1. **manifold-3d v2.5.1 é estrito**. Sempre pré-processar mesh externa antes de subtrair. MeshLab basic chain resolve 95%.

2. **Lazy evaluation engana**. `subtract()` retornar OK não significa que o resultado é válido. SEMPRE testar com `status()`/`getMesh()` antes de assumir sucesso.

3. **Match resolution entre subtraendo e minuendo**. Edge length similar (~0.5mm both) evita slivers.

4. **Ordem de operações importa**. Operações simples (cilindro fino) PRIMEIRO. Operações complexas (mesh detalhada) por ÚLTIMO.

5. **Bake transforms na geometry** quando a API de transform da lib externa for buggy. Three.js Matrix4.applyMatrix4 é confiável.

6. **`mergeVertices` compara TODOS attributes**. Strip pra position-only quando weldar pra topologia.

7. **WASM exceptions vêm como pointers**. Decodificar com `getExceptionMessage(ptr)` quando disponível, ou pelo menos logar o ptr pra debug.

8. **Versionar logs**. `%c[PSI] code build: vN ...` permite diagnose cache stale em 1s.

9. **Per-step try/catch + diagnostic logs entre cada passo**. Vital quando o pipeline tem 5+ passos.

10. **Bbox sanity check após cada operação**. Tamanho esperado vs medido = bug detector instantâneo.
