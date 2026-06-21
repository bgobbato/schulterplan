# PSI — Notas e Ideias Paradas

**Status atual: ✅ RESOLVIDO 31/maio/2026.** Ver `PSI_IMPLEMENTATION.md` pra receita final.

Este arquivo guarda as ideias que NÃO precisamos perseguir agora porque o
manifold-3d (caminho A) funcionou.

---

## Estado final (31/maio/2026)

- **manifold-3d engine**: ✅ funciona end-to-end
  - 13k triangulos, openEdges=0, nonManifoldEdges=0, manifold ✓
  - bone subtraction conforme → pés com concavidade óssea real
  - K-wire furo Ø2.5 atravessando central cylinder
  - ~3-7 segundos por geração

- **three-bvh-csg engine**: alternativa funcional MAS com 14k open edges
  - Validado: STL passa em <https://www.formware.co/onlinestlrepair> e fica manifold
  - Workaround útil se manifold-3d falhar num caso futuro

---

## Caminho que deu certo (resumo)

1. **Pré-processar escapula no MeshLab** → `data/scapula_manifold.obj`
2. **manifoldCylinder via bake-into-vertices** (não usar `.transform(mat3x4)` nem `.rotate([euler])`)
3. **Strip non-position attributes** antes de `mergeVertices` (rim do cilindro precisa soldar)
4. **BONE_OFFSET=0** (evita self-intersections)
5. **K-wire ANTES do osso**, com **16 segments** (matching ~0.5mm edge length)
6. **Per-step diagnostics** (`✓`/`✗` logs) — manifold-3d tem lazy eval, ops booleanas mascaram falhas reais

---

## Ideias paradas (em ordem de promessa, caso precisemos no futuro)

### B — Cilindros de subtração local nos pés
- Em vez de subtrair a escapula inteira, subtrair uma **esfera/cúpula** (Ø ≈ FOOT_DIAMETER × 1.5) centrada em cada `footBase`, dentro do osso.
- Não segue a anatomia exata mas cria concavidade simulada.
- **Vantagem**: funciona com QUALQUER escapula, mesmo não-manifold.
- **Risco**: o "fit" do pé fica genérico (não conformal).
- **Quando usar**: se MeshLab pre-process não for viável (ex: pipeline servidor sem GUI).

### C — Engine híbrido (BVH para osso, depois remanifoldar)
- Usar `three-bvh-csg` só pra subtração óssea.
- Depois passar por "manifoldização" JS:
  - mergeVertices muito agressivo (0.5mm)
  - Close holes (achar loops de open edges, triangular)
  - Recompute normals
- **Quando usar**: se quisermos eliminar o MeshLab pre-process do workflow.
- Próximo doc a escrever: `PSI_CLOSE_HOLES.md` com algoritmo.

### D — Backend automatizado
Quando passar pra produção:
- **D1**: Python + pymeshlab (mesma chain do MeshLab GUI). Roda no pipeline backend uma vez por caso, cacheia em S3.
- **D2**: Node + manifold-3d npm. Roda CSG no servidor.
- **D3**: Servidor faz tudo (geração CSG + manifoldização). Cliente só manda 3 coords + recebe STL.
- Ver `PSI_HAR_ANALYSIS_REPORT.md` — é exatamente o que o CustomedAI faz.

### E — Cosmético/UX (low priority)
- Encurtar K-wire visual (de 200mm → 60mm centrado em kwireBoneEntry) pra cena ficar menos dominada pelo cilindro verde.
- Slider de ajuste pros parâmetros PSI (foot diameter, leg diameter, etc).
- PSI templates (Tripod With Sleeve, etc).

### F — Labels anatômicos embossed nos pés (IDEIA — não implementar ainda)
**Por quê**: o cirurgião precisa identificar visualmente qual pé é anterior vs posterior.
Tipicamente: 3 pernas = **2 anteriores ("A")** + **1 posterior ("P")**. O label evita
ambiguidade no momento de aplicar o guia no campo cirúrgico.

**Geometria proposta**:
- Letter "A" ou "P" embossed no TOPO de cada foot cylinder
- Tamanho: ~3mm char height (cap do foot tem Ø10mm — letra cabe folgada)
- Relevo: 0.6mm (igual ao patient ID, talvez um pouco menos por ser superfície pequena)
- Orientação: virada pra fora (radial), legível quando o cirurgião olha o guia de cima

**Auto-classify A vs P**:
- Precisamos do eixo anterior-posterior (AP) da escapula. Está em
  `payload.axes.scapula.glenoid_ap.vector_xyz` (ou similar — verificar payload real).
- Para cada leg position P_i (em world coords após re-centering):
  - `dotAP = P_i.dot(anteriorAxis)`
  - Se `dotAP > 0`: anterior → letra "A"
  - Se `dotAP < 0`: posterior → letra "P"
- Validar que sai 2A + 1P nos casos típicos. Se sair 3A ou 3P, alertar
  ("legs all on same side — check positioning").

**Como construir o manifold do label**:
1. Pra cada foot, gerar TextGeometry com "A" ou "P" (CHAR_HEIGHT=3mm, depth=0.8mm)
2. Orientar: text +X → tangent radial (ou alinhado com glenoidRight)
   text +Y → K_axis (text "up" aponta pra fora do osso)
   text +Z → K_axis × tangent (extrusion outward)
3. Posicionar: `footTop + K * 0.2mm` (levemente acima do topo, pra ficar visível)
4. Adicionar como primitiva extra no batchBoolean union (junto com patient ID)

**UI**:
- Toggle "Auto-label legs (A/P)" na sidebar Display section, default ON
- (No futuro) override manual via dropdown em cada leg row

### G — Side mark embossed (L/R)
**Por quê**: redundância de segurança — guia traz a indicação de lado.
**Onde**: face oposta do patient ID no central cylinder (180° rotacionado).
**Geom**: letra única "L" ou "R" (case.side do payload), CHAR_HEIGHT=4mm, relevo 0.8mm.
**Quando implementar**: junto com F (labels A/P), num batch de "anatomical labels".

### H — Texto curvado ao redor do cilindro (low priority)
Hoje o patient ID fica em superfície plana tangente ao cilindro. Para Ø10mm e 10 chars,
deviation máx ~0.3mm — aceitável. Mas se aumentarmos pra Ø8mm ou usarmos chars maiores,
fica feio. Solução: deformar a TextGeometry pós-extrusão de forma que cada vertex em (x,y,z)
vire (R·cos(x/R), y, R·sin(x/R)) onde R é o raio do cilindro. Workflow:
1. TextGeometry plana
2. Loop nos vertices, aplica deformação cilíndrica
3. Re-merge vertices (chars adjacentes podem ter vertices coincidentes)
4. geomToManifold

### I — Variante "Tripod With Sleeve" (encaixe para camisa metálica)
**Por quê (uso clínico)**: o cirurgião encaixa um **cilindro metálico** Ø4mm reutilizável
na boca superior do guia. A camisa metálica:
- Protege partes moles ao redor da trajetória do K-wire
- Reforça mecanicamente a guia (PLA/PETG impresso flexiona; metal não)
- Permite uso de brocas/fios mais grossos sem mastigar o guia plástico
- Reutilizável entre cirurgias (esteriliza com a guia metálica em separado)

Esse template corresponde ao "Tripod With Sleeve" do CustomedAI
(ver `PSI_HAR_ANALYSIS_REPORT.md` — templates disponíveis na API
`/api/psitype/{caseId}/case`).

**Geometria proposta**:
- **Camisa**: cilindro Ø4mm × 5mm de profundidade
- **Tolerância**: +0.1mm radial (Ø4.1mm internal) pra fit ajustado mas não preso
- **Posição**: face superior do central cylinder, centrada no K-axis
- **Profundidade**: 5mm a partir da face superior (centralBase + K·CENTRAL_HEIGHT até centralBase + K·(CENTRAL_HEIGHT-5))
- **Interface**: o furo do K-wire (Ø2.5mm) continua mais fundo no plástico, então
  o "encaixe" é só um alargamento na boca. Geometria final na seção transversal:
  ```
  ───┐       ┌───   ← superfície superior do central cylinder
     │       │
     │ Ø4.1  │     ← 5mm de profundidade, cilindro de camisa
     │       │
     ├───┐ ┌─┤     ← step-down para Ø2.5 (furo do K-wire)
     │   │ │ │
     │Ø2.5 │ │     ← continua até a base do guia
     │   │ │ │
     └───┴─┴─┘
  ```

**Implementação CSG** (no `generatePSIManifold`):
- Construir UM cilindro adicional via `manifoldCylinder`:
  ```javascript
  const sleeveBore = manifoldCylinder({
    radius: PSI.SLEEVE_BORE_DIAMETER / 2,    // 4.1mm/2 = 2.05mm
    height: PSI.SLEEVE_BORE_DEPTH,            // 5mm
    axis: g.K,
    center: g.centralBase.clone().add(g.K.clone().multiplyScalar(PSI.CENTRAL_HEIGHT - PSI.SLEEVE_BORE_DEPTH / 2)),
    segments: 24,                             // suficiente pra Ø4mm
    heightSegments: 8,
  });
  ```
- Subtrair APÓS o K-wire e ANTES do osso (mesma estratégia: simples primeiro):
  ```javascript
  if (template === 'tripod-with-sleeve') {
    psi = psi.subtract(sleeveBore);  // alarga a boca pra Ø4.1
  }
  ```

**Novas constants (adicionar ao `PSI` object)**:
```javascript
SLEEVE_BORE_DIAMETER: 4.1,  // Ø metal sleeve + 0.1mm tolerance
SLEEVE_BORE_DEPTH: 5,       // mm — penetra 5mm a partir da face superior
```

**UI**:
- Substituir checkbox simples por **template selector** na sidebar:
  ```
  Template:
  ( ) Tripod (no sleeve) — guia padrão atual
  ( ) Tripod with sleeve — encaixe Ø4mm/5mm para camisa metálica
  ```
- Persistir em `state.template`, default `'tripod'`
- Save no localStorage v3 schema
- Mostrar no skeleton wireframe um indicador visual da boca alargada (anel)

**Patient ID com sleeve — atenção**:
- Hoje o patient ID está em UPPER_RATIO=0.65 do central cylinder
- Com sleeve bore de 5mm = 25% do CENTRAL_HEIGHT 20mm, isso atinge ratio ~0.75-1.0
- O patient ID pode ficar visualmente "cortado" se cair sobre a região alargada
- **Fix**: descer UPPER_RATIO pra ~0.50 quando template = with-sleeve
- OU mover patient ID pra parte INFERIOR (UPPER_RATIO=0.35) — vantagem: cirurgião vê mais quando segura

**Validação geométrica**:
- SLEEVE_BORE_DIAMETER < CENTRAL_DIAMETER? (4.1 < 10 ✓ folga lateral 3mm de plástico)
- SLEEVE_BORE_DEPTH < CENTRAL_HEIGHT - foot-overlap? (5 < 20-3 ✓)
- Wall thickness mínima = (10-4.1)/2 = 2.95mm ≥ 2mm ✓ (suporta print)

**Templates futuros (mesmo mecanismo)**:
- `'humerus-minimal'` (2 legs + shelf) — Humerus PSI template do CustomedAI
- `'humerus-union'` (precision shelf) — Humerus PSI template do CustomedAI
- `'tripod-with-sleeve-locked'` — variante com clip de retenção da camisa

**Quando implementar**: depois de validar clinicamente o tripod simples atual.
A camisa metálica precisa existir fisicamente pra calibrar tolerância — fazer
2-3 protótipos de teste com Ø4.0, 4.1, 4.2 e medir fit.

---

## Para auto-detectar regressão

Adicionar test case em CI futuro:
```javascript
// expected output for the demo case `teste-506460eb`:
// - triangles ≈ 13k ± 2k
// - bbox X 25-35mm, Y 25-35mm, Z 35-45mm
// - openEdges = 0
// - nonManifoldEdges = 0
// - center near (5, -5, -1)
```

Se algum desses falhar, abrir o log e cruzar com a tabela "JORNADA DE ERROS" em PSI_IMPLEMENTATION.md.

---

Related: [[reference-customedai-psi-har]], [[project-psi-features-from-customedai]]
