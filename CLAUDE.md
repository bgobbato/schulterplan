# Claude Project Memory — GPS Web Planner Implantcast

## STATUS: ✅ DEPLOYED TO VERCEL
- **Live**: https://schulterplan.vercel.app/
- **Dashboard**: https://schulterplan.vercel.app/surgery-dashboard.html
- **GitHub**: https://github.com/bgobbato/schulterplan
- **PR**: https://github.com/bgobbato/schulterplan/pull/1

## Projeto
Aplicacao web 3D para planejamento de protese de ombro (glenoide) com implantes
Implantcast Agilon. Single HTML file + Three.js via importmap. Sem build step.

## Tracker oficial: Linear
**Projeto Linear**: [PlanningApp Implantcast FRONTEND](https://linear.app/bgobbato/project/planningapp-implantcast-frontend-31a8b532c894/overview)
- Team Bgobbato (BGO)
- Política dual-source: toda issue Linear espelha em CLAUDE.md ou doc específico (mesma política do PSI)
- 6 épicos ativos: MPR Phase 6 (BGO-68), Import de casos (BGO-69), Back surfaces (BGO-70), Dashboard pipeline (BGO-71), Cleanup (BGO-72), Docs (BGO-73)
- Labels específicas: MPR, PSI, Pipeline, Dashboard, Humerus, 3D-Viewer, Polish, + as gerais (Feature, Bug, etc)

## Planos abertos
- **`MPR_PLAN.md`** v2 — Plano detalhado da implementação MPR (CT). Status: **MVP 1 OK** (Phase 0-2 + coord fix). Branch ativo: `mpr-dev`. Arquivo: `test-heroui-ct.html`.
- **`MPR_HAR_ANALYSIS_REPORT.md`** — Análise CustomedAI (referência arquitetural, Phase 7 Option D).
- **`PSI_IMPLEMENTATION.md`** — Implementação PSI (Phase A+B+C combinadas). **✅ FUNCIONA** com manifold-3d + MeshLab pre-process.

## PSI — estado atual (31/maio/2026 — PIPELINE COMPLETO ✅ + Patient ID)
Arquivo: `test-psi.html` (~1940 linhas). Engine padrão: **manifold-3d** (WASM, manifold ✓).
- 3 spheres draggable na rim, snap automático à superfície da escapula
- Auto-place inicial a 120° no glenoid plane, raio 14mm
- 2 engines: manifold-3d (recomendado) e three-bvh-csg (fallback com repair externo)
- Persistência em `schulterplan_psi_${caseId}` (v2 schema: legs + patientId)
- STL download direto após geração
- **Patient ID embossed** (max 10 chars) na parte superior do cilindro central, ao longo de K, facing lateral. Helvetiker font, char height 1.8mm, relevo 0.8mm.

**Receita CSG (manifold-3d):**
1. Pré-processar `data/scapula.obj` no MeshLab → `data/scapula_manifold.obj` (uma vez por caso)
2. Union de 10 primitives (1 central + 3 feet + 3 legs + 3 fillets) via `batchBoolean('add')`
3. K-wire subtract PRIMEIRO (16 segs, Ø2.5)
4. Bone subtract LAST (offset=0, MeshLab-cleaned)
5. Resultado: ~13k tris, manifold ✓, ~3-7s

**Bugs descobertos e fixados:**
- `Manifold.rotate([euler])` não bate com Three.js Euler XYZ → cilindros tortos
- `Manifold.transform(mat3x4)` v2.5.1 ignora translation → primitivos no origem
- **FIX**: bake transform na geometria THREE.js antes de converter pra Manifold
- `mergeVertices` não solda quando normals divergem → rim aberto. **FIX**: strip non-position attrs
- BONE_OFFSET=0.5 cria self-intersections em concavidades. **FIX**: offset=0
- K-wire 96-seg gera slivers contra bone-conformal surface. **FIX**: 16-seg + ordem invertida (K-wire first)
- Lazy eval: `subtract()` OK não significa resultado válido. SEMPRE testar `getMesh()` na sequência

**Docs PSI (todos no root do projeto):**
- `PSI_IMPLEMENTATION.md` — referência técnica completa (arquitetura, bugs, lições, glossário, changelog)
- `PSI_USER_GUIDE.md` — guia cirúrgico passo-a-passo, linguagem clínica
- `PSI_CODE_MAP.md` — mapa de navegação do test-psi.html (funções, linhas, constants)
- `PSI_TROUBLESHOOTING.md` — FAQ sintoma→fix (17+ casos catalogados)
- `PSI_NOTES.md` — ideias paradas (A-I: subtract dome, BVH manifoldize, backend, A/P labels, sleeve, etc)
- `MESHLAB_PSI_WORKFLOW.md` — passo-a-passo do MeshLab pre-process
- `PSI_HAR_ANALYSIS_REPORT.md` — engenharia reversa do CustomedAI
- `PSI_LINEAR_INDEX.md` — mapeamento issues Linear ↔ docs (cross-reference)

**Tracker oficial do PSI: [Linear project PSI](https://linear.app/bgobbato/project/psi-e52854946bb5)**
Team Bgobbato (BGO). 20 issues criadas (BGO-48 a BGO-67). Política dual-source:
toda ideia/bug nova vai em (a) `PSI_NOTES.md` ou `PSI_TROUBLESHOOTING.md` E (b) issue Linear.

## MPR — estado atual (21/junho/2026 — CONSOLIDADO em test-heroui.html)
A versão `test-heroui-ct.html` foi **promovida ao padrão** e o arquivo deletado.
Agora `test-heroui.html` é a única página principal e inclui tudo: MPR + CT +
cross-section + zip import. (Antiga `test-heroui.html` sem MPR não existe mais —
links de outras páginas continuam apontando pra ela e ganham os recursos do CT
automaticamente.)

## Persistência cross-page do caso importado (21/junho/2026)
Módulo `js/caseStore.js` — IndexedDB wrapper. O zip importado sobrevive a:
- Navegação entre páginas (test-heroui → humerus → dashboard → de volta)
- Hard refresh (Cmd+Shift+R)
- Fechar e abrir o browser

### Como funciona
- DB `schulterplan`, object store `cases`, keyed por `caseId`
- Record: `{ caseId, payload, scapulaObj, humerusObj?, niftiBuffer?, fileName?, savedAt }`
- localStorage `schulterplan_active_case` = caseId atualmente ativo (zero-cost hint)
- API: `saveCase()`, `loadCase()`, `loadActiveCase()`, `setActiveCase()`, `clearActiveCase()`,
  `getActiveCaseId()`, `deleteCase()`

### Integração
- **test-heroui.html**:
  - `applyPipelineCase()` salva no IndexedDB + seta active
  - Init prefere `loadActiveCase()` antes do `fetch('data/...')`
  - Botão "Reset" (topbar) limpa active e recarrega
- **humerus.html**:
  - Init prefere `activeCase.humerusObj` (blob URL) antes do `data/humerus.obj`
  - Cai pro demo se zip não tinha humerus
- **surgery-dashboard.html**:
  - Helpers `getScapulaUrl()`, `getHumerusUrl()`, `getScapulaSourceUrl()`, `getHumerusSourceUrl()`
  - Source URLs caem no planning URL pra imported (sem osteo diff falso)

### Bug crítico que precisou fix: TDZ no init
`MPR` é `const` declarado embaixo do init. Após `await caseStore.loadActiveCase()`
o módulo retoma mas as declarações abaixo do await **ainda estão em TDZ**. Acessar
`typeof MPR !== 'undefined'` lá joga ReferenceError silenciosamente engolido pelo
outer try/catch — resultado: "No default planning data — waiting for import".
**Solução**: ao invés de queue o NIfTI durante init, `initMPR()` (que roda só
quando user clica CT) faz `await caseStore.loadActiveCase()` e pega o `niftiBuffer`
diretamente.

Funciona:
- Botão `CT` na topbar abre coluna 400px com NiiVue 0.69 + NIfTI 64MB (gitignored em `data/`)
- Layout `MULTIPLANAR_TYPE.COLUMN` (axial/coronal/sagittal empilhados)
- Scroll wheel por linha (top=Z axial, mid=Y coronal, bot=X sagittal)
- Crosshair verde em `glenoid_center` exato
- **Toolbar removida** — MPR é view-only (sem W/L, sem pan, sem zoom). Wheel scrolla, pronto.
- Label de coord pipeline + label W/L (read-only) embaixo
- **Overlay do implante (Phase 4C — cross-section real)**:
  - Canvas `#ct-overlay` transparente sobre o NiiVue
  - Three.js renderer próprio + 3 ortho cameras (uma por slice)
  - 3 `LineSegments` (uma por eixo) com `BufferGeometry` pré-alocada
  - Triângulos do implante cacheados em mesh-local (Float32Array 9 floats/tri)
  - Por draw: plano em NiiVue → mesh-local (via inverso de matrix), itera
    triângulos, `intersectTriPlane()` gera 0 ou 2 pontos por tri → upload via
    `setDrawRange` (zero GC pressure)
  - Por viewport: só `.visible` a LineSegments do eixo corrente
  - Pose update (retroversion/inclination/depth) → só recalcula matrix, cache
    de triângulos sobrevive
  - Flag `MPR.useCrossSection` (default `true`) — `false` no console retorna
    ao comportamento Phase 4 (full silhouette via EdgesGeometry) para A/B
  - Edge cases tratados em `intersectTriPlane()`: coplanar, vértice no plano,
    todos no mesmo lado
- **Landmarks removidos** — coords validados, esferas coloridas deletadas do código

**Decisões de design tomadas (31/maio/2026)**:
- **Zoom e pan no NiiVue NÃO serão suportados**. Tentativa de implementar (canvasPos2frac
  para tracking de viewport center + drag handler customizado) quebrou alinhamento do
  implante. Revertido. MPR fica fixo, sem interação a não ser scroll de slice.
- **W/L não será ajustável**. É só visualização — usar defaults do NiiVue.
- **Phase 4C é o default** desde 31/maio/2026 — silhueta cheia disponível só
  via flag console pra debug.

**Conversão de coordenadas pipeline → NiiVue (CRÍTICO)**:
Pipeline xyz_mm está em **LPS** (DICOM convention). NiiVue lê NIfTI como **RAS**.
- `pipelineToNiiVueMM([x, y, z])` = `[-x, -y, z]` (flip X e Y, Z inalterado)
- `sceneToNiiVue` matrix (para implante em scene re-centered):
  ```
  [-1  0  0  -gcX_pipe]
  [ 0 -1  0  -gcY_pipe]
  [ 0  0  1   gcZ_pipe]
  [ 0  0  0     1     ]
  ```
- Validado empiricamente plotando trigonum + 4 rim points

**Lições aprendidas**:
- NiiVue API `moveCrosshairInVox(dx, dy, dz)` é scalars, NÃO array
- `MULTIPLANAR_TYPE.GRID` (default) deixa 4° quadrante vazio mesmo com `multiplanarShowRender: NEVER` — usar COLUMN
- Pipeline é LPS, NiiVue é RAS — flip X e Y para converter (Z mantém)
- Câmera ortho do overlay DEVE ancorar no centro do volume (NiiVue não pan slices)
- `nv.screenSlices[i]` expõe `leftTopWidthHeight` e `fovMM` — usar pra alinhar cameras
- `WebGLRenderer.readPixels` precisa de buffer ativo (após render) — pixels podem
  parecer "0" se ler depois do swap; testar com fresh redraw
- Three.js `function` declarations são reassignáveis em módulos — permite monkey-patch
  de `updateImplantPose` para refresh do overlay
- **NiiVue 0.69 drag modes**: `contrast=1, measurement=2, pan=3, callbackOnly=5,
  roiSelection=6, angle=7, crosshair=8, windowing=9, none=0` — **não existe `zoom`**
  como drag mode (zoom é wheel-based no NiiVue, controlado por `pan2Dxyzmm[3]`)
- **canvasPos2frac + frac2mm** pra tracking de viewport center: parece a abordagem
  certa pra suportar zoom/pan, mas na prática quebra o alinhamento do implante
  (camera ortho do overlay descasa do que NiiVue mostra). Não usar.

## Arquivos Principais

## Arquivos Principais
- `test-heroui.html` — UI principal da escapula (HeroUI dark theme), toda a logica JS inline
- `humerus.html` — pagina de planejamento do umero (dois viewports + lasso para osteofitos)
- `surgery-dashboard.html` — dashboard TV com 6 viewports
- `data/planning_payload.json` — caso de teste pipeline (lado direito, "Teste")
- `data/planning.json` — caso de teste MiriaOE-GPS legado (lado esquerdo)
- `data/scapula.obj` — escapula do paciente (pipeline: NIfTI physical mm coords)
- `data/humerus.exported.obj` — umero do paciente (~12 MB)
- `data/glenoid_anat_2_back.stl` — parte traseira solida do implante Agilon N2
- `UI/` — design system kit exportavel (tokens, CSS, componentes, docs)

## Pipeline Integration (planning_payload.json)
### Regras Criticas de Carregamento
1. **Cache-busting OBRIGATORIO** em todos os fetches de OBJ/STL:
   `loadScapula('data/scapula.obj?v=' + Date.now())`
   O browser cacheia arquivos grandes agressivamente. Sem cache-bust,
   pode servir um OBJ antigo com coordenadas de outro sistema.

2. **Re-centering via Group.position** (NAO modificar vertices):
   ```
   scapulaMesh.position.set(-glenoidCenter.x, -glenoidCenter.y, -glenoidCenter.z);
   scapulaMesh.updateMatrixWorld(true);
   ```
   Evita problemas com buffer upload e funciona com raycasting (matrixWorld propaga).
   Back mesh e ray mesh devem receber a mesma posicao.

3. **P2G translation zeroed** apos re-centering:
   `P2G[3] = P2G[7] = P2G[11] = 0;`
   O implante usa I2P = P2G × adjustM × I2G. Com translation zero,
   implante fica na origem = centro da glenoide.

4. **Implante NAO auto-carrega** em pipeline cases:
   Apenas a escapula carrega no init. O usuario seleciona o implante
   pelos botoes no sidebar (IMPLANT SELECTION cards).

5. **Friedman axis = P2G column 2** (Z reference para implante):
   glenoidNormal = superficie real (do pipeline planes.glenoid_plane.normal_xyz).
   friedmanAxis = direcao 0° retroversao. SAO VETORES DIFERENTES.

### Coordenadas
- OBJ mesh e pipeline xyz_mm estao no MESMO espaco (NIfTI physical mm)
- Pipeline gera OBJ via marching cubes do NIfTI, preservando origin/spacing
- Landmarks xyz_mm = origin + voxel × spacing (calculado pelo pipeline)
- Apos re-centering: glenoidCenter = (0,0,0), tudo relativo a glenoide

## Estado Atual (27/maio/2026)

### O que funciona ✅
- Pipeline `planning_payload.json` carrega corretamente (medidas, landmarks, eixos)
- Escapula re-centrada com glenoide em (0,0,0) via Group.position
- Eixo de Friedman como referencia 0° retroversao (P2G column 2)
- glenoidNormal separado do friedmanAxis (superficie vs referencia)
- Implante posiciona exatamente no centro da glenoide (I2P = P2G rotacao pura)
- Camera "glenoid" olha ao longo do eixo de Friedman
- 6 medidas pre-op exibidas: retroversao, inclinacao, PSI, head radius, NSA, head diameter
- Implante carrega sob demanda (clique no card do sidebar)
- Cache-bust em OBJ para evitar cache de browser
- Adjustments do implante (retroversao/inclinacao/depth) respondem instantaneamente

## Performance — Contact Analysis (27/maio/2026)

### Diagnostico
Ajustes de implante (retroversao, inclinacao, depth) estavam travando ~2.8s sincronamente
apos cada clique. A causa raiz era a **Contact Analysis** rodando depois de cada
adjustment via `scheduleContactUpdate()` (debounce 500ms).

A funcao `analyzeContact()` fazia:
1. Dedup do back surface a CADA chamada (31140 verts → 1586 unique, ~30ms)
2. 1586 raycasts contra glenoidRayMesh (46239 triangulos)
3. ~73 milhoes de testes ray-triangle por analise (THREE.Raycaster e linear, sem BVH)

Resultado: `[PERF contact] analyze=2800ms` bloqueando o render loop.

### Otimizacoes aplicadas
1. **Cache do back surface analysis** (`backSurfaceCache`):
   - dedup, bounds, peg radius — calculados UMA vez por implante
   - cache keyed por `backGeom` identity (referencia, nao copia)
   - invalidado em `setImplant()` quando troca implante
2. **Grid de dedup**: 0.5mm → 1.5mm (9x menos samples: 1586 → ~175)
3. **Raio do glenoid ray mesh**: 35mm → 28mm (menos triangulos no sub-mesh)
4. **Debounce**: 500ms → 800ms (mais tempo pra clicar antes de disparar)

### Resultado
- Antes: ~2800ms por analise (UI travada)
- Depois: ~150-250ms por analise (perceptivel mas aceitavel)
- Click handler: 0.1-0.5ms (instantaneo, sempre foi)

### Diagnostico de performance no codigo
Mantidos logs `console.time` para futura deteccao de regressao:
- `[PERF adjust ...]` em cada clique do botao ajustar
- `[PERF contact] analyze=Xms draw=Yms` apos debounce

### Otimizacoes futuras (se necessario)
- **three-mesh-bvh** — BVH externa para raycast, 100-1000x mais rapido (adiciona dep)
- **Web Worker** — rodar analyzeContact em thread separada (nao bloqueia UI mas mesmo tempo)
- **Reduzir samples ainda mais** (grid 2mm → ~100 samples, ~100ms)
- **Cache de raycast direction** — quando ajuste e pequeno, pular re-raycast

### Proximos Passos (prioridade)

#### 1. LIMPEZA E POLIMENTO da pagina principal
- [ ] Remover esfera vermelha de debug (ainda presente no codigo)
- [ ] Verificar todas as views (anterior, lateral, inferior) com pipeline data
- [ ] Testar Cut Views, Center Line, Measure, Transparency com a nova geometria
- [ ] Testar Contact Analysis (precisa back surface — so funciona com Agilon N2)
- [ ] Garantir que Import (drag-and-drop) tambem aplica cache-bust e re-centering

#### 2. IMPORT FROM ZIP / FOLDER
- [ ] Implementar import de `planning_package.zip` (output do pipeline)
  - Zip contem: planning_payload.json + models/scapula_planning.obj + models/humerus_planning.obj
  - Ao importar, extrair e aplicar `parsePipelinePayload` + re-centering
  - Usar JSZip ou File API para ler o zip no browser
- [ ] Atualizar `applyImportedCase()` para suportar pipeline format
  - Deve aplicar as mesmas regras: cache-bust, Group.position, P2G zeroing

#### 3. PAGINA DO UMERO (humerus.html) — Pipeline Integration ✅ (27/maio/2026)
- [x] Carrega `data/humerus.obj` da pipeline com cache-bust
- [x] Orientacao anatomica via landmarks + scapula AP axis:
  - World +Y = vertical (canal_distal → head_center)
  - World +Z = anterior (glenoid_ap projetado ⟂ Y)
  - World +X = lado direito do paciente (right-handed)
- [x] Bbox re-centrado em (0,0,0) — bone visualmente centralizado
- [x] Views anterior/lateral usam eixos anatomicos fixos:
  - Anterior: camera em +Z
  - Lateral: camera em +X (R) ou -X (L), depende de `case.side`
- [x] 7 medicoes do pipeline exibidas no sidebar:
  - Humerus: head_radius, head_diameter, NSA, posterior_subluxation, posterior_offset
  - Scapula: retroversion, inferior_inclination
- [x] Badge `pipeline` (roxo) diferencia medidas do payload vs computed locais
- [ ] Selecionar quais medidas manter (todas estao visiveis por enquanto)
- [ ] Eventualmente: visualizar landmarks no 3D, implant planning do umero

### Funcoes-chave de orientacao no humerus.html
- `buildAnatomicalRotation(head, distal, apAxis)` — constroi Matrix4 (Y=vertical, Z=anterior, X=right)
- `state.pipelineLandmarks` — dict de Vector3 com landmarks no novo frame mundial
- `state.side` — 'R'/'L', usado por `fitCameraToView` para lateral e por cut plane

### Neck Cut Plane 135° (humerus.html) ✅ (27/maio/2026)
- Plano de corte verde semi-transparente, normal a 135° do eixo do canal (+Y mundial)
- Posicionado em `anatomic_neck_center` (do payload), tamanho 80x80mm
- Inclinado para o lado lateral (lateralSign × cos45°, -cos45°, 0):
  - RIGHT shoulder → normal aponta para (+X, -Y)
  - LEFT shoulder → normal aponta para (-X, -Y)
- **Controles no sidebar direito** ("Neck Cut Plane (135°)"):
  - Checkbox "Show plane" — toggle visibilidade
  - **Offset (sup/inf)**: botoes ↓ ↑ deslocam ±1mm ao longo de +Y
  - **Tilt (sagittal)**: botoes ⟲ ⟳ rotacionam ±2° em torno do eixo X (eixo AP)
    - ⟲ (forward): anterior edge desce
    - ⟳ (back): anterior edge sobe
  - "Reset offset & tilt" — zera ambos
- O plano amarelo (`humeral_neck_plane_auto` from landmarks) foi testado mas removido
  por nao parecer anatomicamente bem posicionado. Codigo removido.

### Funcoes-chave de cut plane (humerus.html)
- `createCutPlanes(payload)` — cria o plano em ambos viewports apos carregar pipeline
- `updatePlane135()` — recomputa posicao + orientacao do offset + tilt
- `shiftPlane135(deltaMm)`, `tiltPlane135(deltaDeg)`, `resetPlane135()`
- `state.plane135BaseCenter` / `state.plane135BaseNormal` — referencia imutavel
- `state.plane135Offset` / `state.plane135TiltDeg` — ajustes do usuario

### Medular Mode — Auto-Wireframe (27/maio/2026)
- Ao clicar "Medular", ativa wireframe automaticamente (canal fica mais visivel)
- Ao sair, restaura o estado anterior do wireframe (`state._wireframeBeforeMedular`)
- `state.side` — 'R'/'L', usado por `fitCameraToView` para lateral

#### 4. NIfTI MPR VIEWER (CT visualization)
- [ ] Integrar NiiVue.js para visualizacao de cortes CT (axial/coronal/sagittal)
- [ ] O pipeline exporta `processing/selected_series_0000.nii.gz` (volume CT compacto)
- [ ] Sincronizar plano de corte com posicao do implante
- [ ] Overlay de landmarks nos cortes

#### 5. SURGERY DASHBOARD — Osteophyte Comparison ✅ (parcial, 27/maio/2026)
- [x] Substituir placeholders (humerus + osteo) por 4 viewports de comparacao
- [x] Layout: humerus-panel mostra umero with/without; vp-osteo mostra scapula with/without
- [x] Algoritmo de diff por hash de triangulos (precisao 0.01mm):
  - Triangulo do source presente no planning → osso branco normal (mantido)
  - Triangulo do source AUSENTE no planning → osteofito amarelo translucido
- [x] Umero aplica anatomicalMatrix + edits do lasso salvos em localStorage
- [x] Testado para umero — funcionando
- [ ] Testar escapula apos fazer resseccao (usuario ainda nao removeu osteofitos da escapula)
- [ ] Melhorar dashboard:
  - [ ] Camera angles melhores
  - [ ] Talvez adicionar contagem de triangulos removidos no header
  - [ ] Sincronizar rotacao dos pares with/without (rotaciona um, rotaciona o outro)

#### 5b. SURGERY DASHBOARD — outras melhorias futuras
- [ ] Pipeline data ao inves de planning.json legado nos viewports do implante
- [ ] CT MPR (NiiVue) em viewports extras

### Persistencia de osteofitos (27/maio/2026, expandido 28/maio/2026)
- **humerus.html**: lasso salva removed triangles em localStorage com cache-bust
  - Key: `schulterplan_humerus_edit_${caseId}`
  - Payload: `{ version, caseId, side, savedAt, anatomicalMatrix, triangleCount, removedB64 }`
  - `anatomicalMatrix` (16 floats) = transform OBJ → world (rotation + bbox-recenter)
  - `removedB64` = Float32Array de triangulos removidos (9 floats por tri) em base64
  - Debounce 400ms entre lasso e save
  - Hash de triangulos com 3 casas decimais para restore (`triHash` function)
- **Restore**: ao reabrir humerus.html, le localStorage e re-aplica edits via hash matching
- **test-heroui.html (scapula)** ✅ (28/maio/2026): lasso portado do humerus
  - Botao "Remove Osteophytes" no sidebar esquerdo (nova secao)
  - SVG overlay (`#scapula-lasso-svg`) sobre o viewer (z-index 50, pointer-events:none)
  - `controls.enabled = false` enquanto lasso ativo (sem orbit conflitando)
  - Esc cancela o modo lasso
  - Key: `schulterplan_scapula_edit_${caseId}`
  - Payload: `{ version, caseId, side, savedAt, groupOffset, triangleCount, removedB64 }`
  - `groupOffset` = `[-rawCenter.x, -rawCenter.y, -rawCenter.z]` (offset do Group da escapula)
  - **Removed triangles salvos em LOCAL frame (raw NIfTI mm)** — diferente do humerus que salva em world
  - Undo (max 50 snapshots) + Reset (`scapulaLasso.originalPositions`)
  - Apos cada operacao: `glenoidRayMesh = null` e `backSurfaceCache = null` para invalidar caches de contact

### Persistencia de implante + scenarios (28/maio/2026)
- **test-heroui.html**: implante selecionado + ajustes + scenarios salvos automaticamente
  - Key: `schulterplan_implant_${caseId}`
  - Payload: `{ version, caseId, side, savedAt, selectedImplant, adjust, scenarios }`
  - Save acontece em: `setImplant()`, cada clique de ajuste (`.ctrl-btn[data-axis]`), reset, save scenario
  - Debounce 350ms para evitar writes excessivos em sequencia de cliques
  - Restore no init: se houver state salvo, override `state.selectedImplant`, `state.adjust`, `state.scenarios`
  - Se `savedImplantState.selectedImplant` existe, auto-carrega o implante (mesmo em pipeline cases)

### Comentarios (test-heroui.html)
- Ja salvavam em `schulterplan-comments-${caseId}` (formato antigo, hifen)
- Tambem em `schulterplan-comments-latest` (objeto com caseId + comments + savedAt)
- Lidos pelo surgery-dashboard.html no Planning Summary

### Arquivos copiados do pipeline para data/ (27/maio/2026)
- `data/scapula_source.obj` (8.9M) = decimated_hu150/scapula_smooth_largest_decimated.obj
- `data/humerus_source.obj` (6.9M) = mild_smooth_hu150/humerus_smooth.obj
- (`data/scapula.obj` e `data/humerus.obj` continuam sendo os planning_obj)

### Auto Measure (test-heroui.html) — landmarks (28/maio/2026)
- Antes: raycasting do implante para o rim da glenoide
- Agora: implant center → `glenoid_inferior.xyz_mm` (laranja) e `glenoid_anterior.xyz_mm` (ciano)
- Landmarks vem de `state.planning._pipelinePayload.landmarks.scapula`
- Conversao para world: `landmark.xyz_mm + scapulaMesh.position` (que e `-rawCenter`)
- Sem projecao na superficie — implant center pode estar fora da glenoide
- Cada medicao tem `m.label = 'Inferior' / 'Anterior'`

### Surgery Dashboard — pipeline-aware (28/maio/2026)
- Init agora tenta `planning_payload.json` primeiro, fallback para `planning.json` legacy
- `planningFromPipelinePayload(payload)` sintetiza um objeto `planning` no mesmo shape do legacy
  - P2G construido via Friedman axis (Z) + glenoid_si orto (Y) + cross (X)
  - I2G = identity, translation = glenoid_center.xyz_mm
- `buildAdjustMatrix(adj)` portado de test-heroui.html (Euler XYZ + setPosition)
- `buildI2P(p, adjust)` agora aplica adjust: `I2P = P2G × adjustM × I2G`
- Le `schulterplan_implant_${caseId}` para sobrescrever selectedImplant + adjust
- Info card mostra valores finais (base + adjust): retroversion, inclination, depth
- Osteo viewport da escapula aplica edits do `schulterplan_scapula_edit_${caseId}` ao planArr antes do diff
  - Subtrai glenoid_center dos removed_floats (que estao em raw NIfTI mm)
  - Hash-match e remove do planArr → osteo amarelo inclui o que pipeline removeu E o que usuario removeu

### Arquivos copiados do pipeline para data/ (27/maio/2026)
- `data/scapula_source.obj` (8.9M) = decimated_hu150/scapula_smooth_largest_decimated.obj
- `data/humerus_source.obj` (6.9M) = mild_smooth_hu150/humerus_smooth.obj
- (`data/scapula.obj` e `data/humerus.obj` continuam sendo os planning_obj)

### Flush de saves na navegacao (28/maio/2026)
**Bug critico resolvido**: saves debounced (350-400ms) eram perdidos quando o usuario
navegava entre paginas rapido. Refatorado para separar escrita vs debounce:

- `_writeXNow()` (sincrono) — escreve no localStorage agora
- `saveX()` (debounced) — agenda escrita via setTimeout
- `flushXSave()` — cancela timer e escreve agora

Em `test-heroui.html` e `humerus.html`:
- `window.addEventListener('beforeunload', flushAllSaves)`
- `window.addEventListener('pagehide', flushAllSaves)` (iOS Safari)
- `document.querySelectorAll('.topbar a[href]').forEach(l => l.addEventListener('click', flushAllSaves))`

Cobre: navegacao por link, fechar aba, recarregar.

### Cut plane persistente (28/maio/2026)
- `humerus.html` agora salva `plane135Offset` + `plane135TiltDeg` dentro do
  `schulterplan_humerus_edit_${caseId}` (mesma chave do osteo).
- Os botoes ↑↓⟲⟳ disparam `saveHumerusEdit()` automaticamente.
- Init restaura ambos via `loadHumerusEdit()` e chama `updatePlane135()`.

### Dashboard — Painel do umero redesenhado (28/maio/2026)
- **Antes**: 2 sub-viewports (Humerus With / Without) empilhados
- **Agora**: 1 viewport unico (`canvas-humerus-main`) com 3 botoes no header:
  - **Original** (mode): mostra `srcArr` em branco solido (umero completo com osteo)
  - **Osteophytes** (mode, default): mostra `keptGeom` + `osteoGeom` em amarelo
  - **Osteotomy** (toggle): plano de corte verde 135°

Tres meshes coexistem na cena (sourceMesh, keptMesh, osteoMesh) — toggle via `.visible`.
- O `cutPlaneMesh` usa `plane135Offset` + `plane135TiltDeg` do localStorage
- Centro do plano = `anatomic_neck_center.xyz_mm` * anatomicalMatrix (frame mundial)
- Normal = `(lateralSign * cos45°, -cos45°, 0)` com tilt aplicado em torno do X

CSS `.hm-btn` + `.hm-btn.active` no header — botoes pequenos uppercase com cor indigo quando ativos.

### Dashboard — Layout reorganizado (29/maio/2026)
- Grid antes: `180px 1fr 1fr 1fr` (4 colunas)
- Grid agora: `180px 360px 1fr 1fr 1fr` (5 colunas)
- **Col 1** (180px): `.implant-info-col` — card "Glenoid Implant" (span 2 rows)
- **Col 2** (360px): `.humerus-col` — card "Humerus" com 3 botoes visiveis (span 2 rows)
- **Cols 3-5** (1fr cada): os 6 viewports da escapula (3x2 grid)
- `.humerus-mode-buttons` ganhou `flex-wrap:wrap` no header para responsividade
- Ordem cirurgica: implant info → umero → escapula (esquerda para direita)

### Dashboard — Reorganizacao completa (29/maio/2026)
**Grid final 5 colunas × 2 rows**:
- Col 1 (160px): `.implant-info-col` — card "Glenoid Implant" info (span 2 rows)
- Col 2 (320px): `.humerus-col` — card "Humerus" com 3 botoes mode (span 2 rows)
- Col 3 (320px): `.scapula-col` — card "Scapula — Glenoid" combinado (span 2 rows)
- Col 4 (1fr): `#vp-implant` — "Scapula + Implant" (span 2 rows)
- Col 5 (1fr): `#vp-cl-inf` (row 1) + `#vp-cl-lat` (row 2)

**Paineis removidos**: vp-measure (Auto Measure) e vp-osteo (Scapula Osteo with/without) — funcionalidade consolidada no Scapula Glenoid combinado.

### Dashboard — Scapula Glenoid combinado (29/maio/2026)
Substituiu os 3 paineis antigos (Scapula glenoid, Auto Measure, Scapula osteo) por UMA viewport com 3 botoes mode no header:
- **Original**: source.obj em branco solido (com osteofitos)
- **Osteophytes** (padrao): kept (white) + osteo (yellow overlay) — diff hash-based
- **Measurements**: kept (white) + esferas/linhas das medidas (implant center → glenoid_inferior em laranja, → glenoid_anterior em ciano) + overlay com tags `Inferior: X mm` / `Anterior: Y mm`
  - **Implante OCULTO** neste modo (so esferas+linhas, foco nas medidas)

Camera no glenoid view:
- viewDir = `(P2G[2], P2G[6], P2G[10])` = Friedman axis (P2G col 2)
- up = `(P2G[1], P2G[5], P2G[9])` = glenoid Up
- LookAt = (0,0,0) = centro da glenoide (apos re-centering)

Equivalente ao `setViewFn('glenoid')` em test-heroui.html.

### Dashboard — init sequencial (29/maio/2026)
**Bug**: init() e initOsteophyteComparison() rodavam em PARALELO. `initOsteophyteComparison` precisava de `_implantGeomShared`, `_i2pShared`, `_payloadShared` que so eram setados pelo init() — race condition.

**Correcao**: serializar via top-level await:
```javascript
(async () => {
  await init();
  await initOsteophyteComparison();
  wireFullscreenButtons();
})();
```

Tambem hoisted `_implantGeomShared`, `_i2pShared`, `_payloadShared`, `_planningShared` no escopo do modulo.

### Dashboard — Camera com aspect ratio do viewport (29/maio/2026)
O painel do umero estava muito zoom-in porque o calculo de distancia da camera ignorava o aspect ratio do canvas. Como a coluna do umero e muito mais alta que larga (aspect ~0.55), `dist_for_width = halfW / (tan(fov/2) * aspect)` e MAIOR que `dist_for_height` para o mesmo osso.

```javascript
const aspect = canvas.width / canvas.height;
const distForHeight = halfH / Math.tan(fovRad / 2);
const distForWidth  = halfW / (Math.tan(fovRad / 2) * aspect);
const dist = Math.max(distForHeight, distForWidth) * 1.5;
```

### Dashboard — Matriz anatomica computada (29/maio/2026)
Se o usuario nao tinha aberto `humerus.html` ainda com o caso atual, `schulterplan_humerus_edit_${caseId}` nao existia, entao o dashboard caia no fallback de bbox-center (sem rotacao). O bone ficava deitado.

Correcao: se nao houver matriz salva, COMPUTAR direto dos landmarks do payload usando a mesma logica de `buildAnatomicalRotation` do humerus.html:
- Y = head_center - canal_distal (normalizado)
- Z = glenoid_ap projetado ⟂ Y
- X = Y × Z

Resultado: osso fica vertical mesmo sem o usuario ter aberto humerus.html.

### Dashboard — Botoes Fullscreen (29/maio/2026)
Cada um dos 5 paineis principais tem agora um botao `.fs-btn` no card-header (icone ⤢ com 4 cantos):
- card-humerus, card-scapula, vp-implant, vp-cl-inf, vp-cl-lat

Wire generico:
```javascript
btn.addEventListener('click', () => {
  if (document.fullscreenElement === card) document.exitFullscreen();
  else card.requestFullscreen();
});
document.addEventListener('fullscreenchange', () =>
  setTimeout(() => window.dispatchEvent(new Event('resize')), 80));
```

CSS `:fullscreen` ajusta o card para 100vw × 100vh com canvas filling. O resize automatico do `createViewport` (que escuta `window resize`) re-fita o renderer/camera para as novas dimensoes.

### Bug critico: TDZ (Temporal Dead Zone) no restore (29/maio/2026)
**Sintoma**: ao voltar do umero para a escapula, ou ao recarregar a pagina apos
fazer alteracoes, tudo voltava ao estado inicial. Save funcionava, restore nao.

**Causa raiz**: o init do `test-heroui.html` tem `await fetch` (top-level await).
Quando esse await retoma, ele chama `restoreScapulaEdit()` e `setImplant()`,
que por sua vez acessam `scapulaLasso`, `_implantSaveDebounce`, etc.

Essas variaveis estavam declaradas com `const`/`let` DEPOIS do init no script.
Com top-level await, o modulo pausa no await; quando retoma, o codigo abaixo
ainda nao foi executado, entao os `const`/`let` ainda estao em TDZ.

`function` declarations sao hoisted mas seus CORPOS sao avaliados no momento
da chamada. Se o corpo referencia um `const` em TDZ, gera erro:
`Cannot access 'X' before initialization`. O erro era engolido pelo
try/catch do init, mostrando apenas no console:
`No default planning data — waiting for import. Cannot access 'scapulaLasso'...`

**Correcao**: mover as declaracoes que o init usa para o TOPO do script
(logo apos `const state`), antes do init:
```javascript
const IMPLANT_STATE_KEY = (caseId) => `schulterplan_implant_${caseId}`;
const SCAPULA_EDIT_KEY  = (caseId) => `schulterplan_scapula_edit_${caseId}`;
let _implantSaveDebounce = null;
let _scapulaSaveDebounce = null;
const scapulaLasso = { mode: false, points: [], removedFloats: [], undoStack: [], originalPositions: null, drawing: false };
```

**Licao**: em ES modules com top-level await, NUNCA confiar que declaracoes
abaixo do await ja foram executadas. Quando init precisar de uma variavel,
declarar antes do try/catch que tem o await.

#### 6. BACK SURFACE MODELS (para contact analysis)
- [ ] Criar back surfaces para implantes alem do Agilon N2:
  - Agilon Anat. 3 Short, Agilon Anat. 3 Long, Agilon Round 3, TechImport
- [ ] Extrair do Effigos Explorer (mesma origem dos STLs principais)
- [ ] Adicionar a IMPLANT_CORRECTIONS e BACK_SURFACE_MAP

#### 7. DEPLOY ATUALIZADO
- [ ] Commitar todas as mudancas no GitHub (branch pipeline-integration)
- [ ] PR para main com descricao das mudancas
- [ ] Atualizar Vercel deploy

### Arquitetura do Pipeline Flow
```
Pipeline Output (planning_package/)
  ├── planning_payload.json      → parsePipelinePayload() → state.planning
  ├── models/scapula_planning.obj → loadScapula() + re-center via Group.position
  ├── models/humerus_planning.obj → humerus.html (futuro)
  └── processing/selected_series_0000.nii.gz → NiiVue (futuro)

Init Flow (test-heroui.html):
  1. Fetch planning_payload.json (pipeline) ou planning.json (legacy)
  2. parsePipelinePayload() → state.planning com P2G, I2G, preOp measurements
  3. loadScapula() com cache-bust → scene.add(scapulaMesh)
  4. Extract axes: friedmanAxis, glenoidNormal, glenoidUp, glenoidRight
  5. Re-center: scapulaMesh.position = -rawCenter, zero P2G translation
  6. Build back mesh com mesma position offset
  7. Camera "glenoid" ao longo do friedmanAxis → viewDistance = 80mm
  8. Implante: usuario seleciona via sidebar card → setImplant() → updateImplantPose()
  9. I2P = P2G(rotation only) × adjustM × I2G(identity) → implante na origem
```

## Pagina do Umero (`humerus.html`)
**Doc completa em `HUMERUS.md`.** Resumo:
- Layout: sidebar esquerda (medidas) + DOIS viewports lado-a-lado + sidebar direita (ferramentas)
- Viewport esquerdo: SEMPRE anterior (fixo)
- Viewport direito: switchable (lateral / anterior / superior / inferior) via segmented control no topbar
- Ambos os meshes compartilham UMA `BufferGeometry` — edicao propaga automaticamente
- **Auto-orientacao**: detecta longAxis e headEnd via bbox + densidade de vertices, robusto a qualquer convenção de eixo do OBJ
- Medidas:
  - Head radius — auto-fit de esfera nos 18% superiores do eixo longo
  - Cervico-diaphyseal angle — placeholder (precisa landmarks manuais)
  - Medullary canal Ø — heuristica via bbox
  - Cortical thickness — placeholder
- **Ferramenta Lasso ("Remove Osteophytes")**:
  - Botao ganha glow ambar + cursor lasso SVG + label "Lasso Active" quando ativo
  - Captura poligono SVG em tela, projeta centroide de cada triangulo, point-in-polygon
  - **Highlight em tempo real**: triangulos dentro do laco ficam pintados em vermelho semi-transparente em AMBOS os viewports antes de soltar
  - Centroides pre-projetados UMA vez no pointerdown (camera travada) — preview instantaneo mesmo com 200k+ tris
  - Geometria nao-indexada para splice trivial
- **Undo / Reset / Showing Original** — TRES controles distintos:
  - Undo: pop do stack (max 50 snapshots Float32Array), Cmd/Ctrl+Z
  - Reset: confirma, clona originalGeometry, esvazia stack
  - Showing Edited/Original: NAO muta dados — apenas troca ponteiro de geometria + tinge original em azul
- **Medular**: clipping plane no renderer do viewport direito, perpendicular ao longAxis em midpoint (origem). Camera se move pra olhar de cima da cabeca, label muda pra "medullary · axial", segmented control fica desabilitado
- Atalhos: Esc cancela modo ativo, Cmd/Ctrl+Z desfaz

## Como trocar o modelo 3D do umero
Caminho mais simples: substitui `data/humerus.exported.obj` por outro OBJ e recarrega a pagina. Auto-detect cuida do resto. Ver `HUMERUS.md` §5 para alternativas e knobs por modelo.

## Sistema de Coordenadas
- GPS Exactech: peg em -Z, +X lateral, +Y superior, +Z anterior
- STLs Implantcast Agilon: peg em +X (precisa ry90 para converter)
- `glenoidNormal` aponta PARA FORA do osso (direcao do espaco articular)
- "Into bone" = `-glenoidNormal`
- Depth+ move implante em +glenoidNormal (afasta do osso)

## Bone Contact Analysis
- Usa **raycasting** (Three.js Raycaster) com sub-mesh da glenoide
- Amostragem baseada nos vertices do **back surface model** (parte traseira solida do implante)
- O back surface e invisivel, segue a posicao do implante (mesma matrix I2P)
- Thresholds calibrados: depthThreshold=0.5mm, embedded<-1mm, contact<0, near<0.5mm

## PENDENCIA IMPORTANTE: Back Surface Models
Apenas o **implante Agilon N2** tem back surface (`glenoid_anat_2_back.stl`).
O usuario (Dr. Bruno Gobbato) precisa criar os back surfaces para os outros implantes:
- [ ] Agilon Anat. 3 Short → `glenoid_anat_3_short_back.stl` (a criar)
- [ ] Agilon Anat. 3 Long → `glenoid_anat_3_long_back.stl` (a criar)
- [ ] Agilon Round 3 → `glenoid_round_3_back.stl` (a criar)
- [ ] TechImport → `techimport_back.stl` (a criar)

Cada back surface deve ser:
1. A parte traseira do implante em formato solido (a face que encosta no osso)
2. Extraido do Effigos Explorer (mesma origem dos STLs principais)
3. Adicionado a `IMPLANT_CORRECTIONS` com center e rot adequados
4. Adicionado a `BACK_SURFACE_MAP` no JS (mapeia tipo → arquivo)
Sem o back surface, a analise de contato NAO funciona para esse implante.

## Center Line
- Linha verde no centro do implante, atravessa toda a escapula
- Direcao = eixo do peg (local -Z → world), 80mm cada lado
- `depthTest: false`, `renderOrder: 999`
- Toggle via botao "Center Line", permanece com implante off
- Atualiza em `updateImplantPose()` e `updateCenterLine()`

## Ferramenta de Medicao 3D
- Modo ativado por botao "Measure", cursor vira crosshair
- Click em 2 pontos na superficie 3D (raycasting contra scapula + implante)
- Esferas magneticas (r=1.2mm, depthTest:false, renderOrder:998) + linha conectando
- 6 cores rotativas: `MEASURE_COLORS` = [cyan, laranja, amarelo, roxo, verde, rosa]
- Lista de medicoes com distancia em mm, delete individual ou "Clear All"
- Deteccao de drag (5px threshold) via mousedown/mouseup — evita confundir com orbit
- Funcoes: `onMeasureClick()`, `createMeasureSphere()`, `createMeasureLine()`, `finishMeasurement()`, `removeMeasurement()`, `clearAllMeasurements()`, `updateMeasureUI()`

## Auto Measure
- Botao "Auto Measure" mede distancia do centro do implante ao rim da glenoide
- Inferior (laranja): centro → rim inferior (-glenoidUp)
- Anterior (cyan): centro → rim anterior (glenoidRight, testa ambas direcoes)
- Raycasting contra glenoidRayMesh com sistema multi-offset (4.0, 2.5, 1.5mm)
  - Offset alto passa por cima da concavidade e acerta o rim real
  - Fallback para offset menor se o rim for mais baixo naquela direcao
- Esferas projetadas no plano da face glenoidal + 2mm offset (surfaceOffset)
- Valores esperados: 12-26mm
- Funcoes: `runAutoMeasure()`, `clearAutoMeasure()`, `castAtBestOffset()`

## Cut Views — Vistas de Corte (Session 6) ✅
- Planos axial, coronal e sagittal exatamente no plano do implante
- **Selective clipping**: apenas escápula é cortada, implante permanece inteiro
- Implementação: `scapulaMaterial.clippingPlanes` + `scapulaBackMaterial.clippingPlanes`
- BackSide mesh renderiza superfícies internas com cor escura (#6b5e4a)
- Câmera se reposiciona automaticamente: axial→inferior, coronal→anterior, sagittal→lateral
- Mapeamento: axial=glenoidUp, coronal=glenoidRight, sagittal=glenoidNormal
- Botão abreviado: "Cut" (antes "Cut View")

## Voice-to-Text Comments (Session 6) ✅
- SpeechRecognition API do navegador para gravação e transcrição automática
- Suporta PT-BR e EN-US com toggle visual (🇧🇷/🇺🇸)
- Persistência em localStorage com chave `schulterplan_comments_${caseId}`
- Cada comentário armazena: text, timestamp, language
- UI com botão microfone + lista de comentários com timestamps
- Funciona com Chrome, Safari, Edge (navegadores com SpeechRecognition nativa)

## Planning Summary no Surgery Dashboard (Session 6) ✅
- Resumo automático dos comentários de planejamento no AI panel
- Extrai "Key Findings" de padrões como "• " ou "- " nos comentários
- Sincronização automática via localStorage com caseId
- Exibição de comentários com timestamp, idioma e texto
- CSS com tema visual integrado ao dark mode

## Topbar Otimizada (Session 6) ✅
- Labels abreviados para evitar compressão visual
- Espaciamento reduzido: padding 14px, gap 6px (antes 20px/12px)
- Botões menores (btn-sm): 5px 10px padding (antes 6px 14px)
- Nenhuma perda de funcionalidade, apenas visual compactada

## Decisoes Tecnicas
- Vanilla JS (sem React) — `type="module"` incompativel com `text/babel`
- importmap para Three.js r160 via unpkg CDN
- IMPLANT_CORRECTIONS: rotacao por modelo (ry90 para Agilon, rx180 para TechImport)
- Matriz I2P = P2G x adjustM x I2G_orig
- `patientRefToGlenoidRef` transforma Glenoid→Patient (nome enganoso, NAO inverter)
- ClippingPlanes per-material para selective clipping (não global)
- localStorage para persistência de comentários cross-page
- Web Speech API para voice-to-text (nativa do navegador, sem servidor)
