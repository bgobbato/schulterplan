# PSI Troubleshooting — Erros comuns + Fixes

FAQ baseado nos 6+ bugs encontrados na implementação. Se um caso futuro falhar,
procura o sintoma aqui antes de mergulhar no código.

---

## Sintomas → Diagnóstico → Fix

### 1. `[PSI Init] Error: No planning_payload.json`
**Causa**: faltando `data/planning_payload.json` na pasta data/, ou estrutura inválida.
**Fix**:
- Confirma arquivo existe: `ls data/planning_payload.json`
- Confirma JSON válido: `cat data/planning_payload.json | python3 -m json.tool`
- Confirma servidor servindo data/: `curl http://localhost:8080/data/planning_payload.json | head`

---

### 2. Escapula carrega mas sem cor/textura, modelo invisível
**Causa**: OBJ não tem normals, ou material foi sobrescrito.
**Fix**:
- Verificar no console: `scapulaMesh.children[0].material` deve ser MeshPhongMaterial
- Re-exportar OBJ com normals do MeshLab ou pipeline

---

### 3. Esferas das pernas aparecem mas drag não funciona
**Causa**: `controls.enabled` ficou false e não voltou. Ou `state.draggingLeg` travou.
**Fix**:
- Console: `state.draggingLeg = -1; controls.enabled = true;`
- Ou recarrega a página (estado limpa)

---

### 4. HUD: `bone subtract skipped: Not manifold`
**Causa**: `data/scapula_manifold.obj` ausente OU não foi cleaned no MeshLab.
**Fix**:
- Roda workflow MeshLab (`MESHLAB_PSI_WORKFLOW.md`)
- Salva como `data/scapula_manifold.obj`
- Hard refresh (Cmd+Shift+R)
- Verifica console: `[PSI Init] Using data/scapula_manifold.obj (cleaned variant)`

---

### 5. HUD: `14609 open · 3 non-manifold edges` (vermelho)
**Causa**: você está no engine `three-bvh-csg`. Resultado tem T-junctions.
**Fix**:
- Opção A: troca pro engine `manifold-3d` (sidebar Engine section)
- Opção B: aceita e usa repair externo (formware.co)

---

### 6. Console: `Generation failed: 536280` (ou outro número grande)
**Causa**: WASM exception pointer. Manifold-3d v2.5.1 não decodifica direito.
**Fix**:
- Console agora tem `decodeErr` automaticamente
- O log granular mostra qual passo travou (`status()`/`getMesh()`)
- Causa comum: slivers de interseção K-wire×osso. Garante:
  - K-wire com 16 segments (não 96)
  - Ordem: K-wire ANTES de bone (já é o padrão)
  - BONE_OFFSET = 0 (não 0.5)

---

### 7. Console: `Generation failed: Not manifold` na criação de primitivos
**Causa**: `THREE.CylinderGeometry` tem normals divergentes no rim. `mergeVertices`
não solda → rim aberto → manifold rejeita.
**Fix**:
- Já tratado em `geomToManifold` (strip non-position attrs antes do weld)
- Se voltar: confirma que `geomToManifold` tem o block "stripped = new BufferGeometry()"
  com só position e index

---

### 8. Cilindros saem TODOS no origem (bbox center=0,0,0 mas tamanho enorme)
**Causa**: usar `manifold.transform(mat3x4)` v2.5.1 — translation se perde.
**Fix**:
- Usa abordagem `bake-into-vertices` em `manifoldCylinder`:
  ```javascript
  geom.applyMatrix4(mat4);  // bake no THREE.js
  return geomToManifold(geom);  // sem transform/rotate
  ```
- Já é o padrão v10

---

### 9. Tripod sai "torto" / "asterisk-like" no viewer
**Causa**: cilindros mal orientados. Provavelmente `manifold.rotate([euler])` usado
em algum lugar.
**Fix**:
- Procura por `.rotate([` no código — deve estar SÓ em comentários históricos
- Confirma `manifoldCylinder` usa `applyMatrix4` no THREE.js geom

---

### 10. Generate funciona mas STL aberto no slicer tem buracos
**Causa**: STL exportado pelo BVH engine sem repair.
**Fix**:
- Confirma `manifold ✓` no HUD ANTES de baixar
- Se for BVH, upload para `formware.co/onlinestlrepair`

---

### 11. Patient ID input não persiste
**Causa**: localStorage cheio, ou caseId mudou entre sessions.
**Fix**:
- DevTools → Application → Local Storage → `schulterplan_psi_*` — confirma chave existe
- Confirma key version=2 no JSON
- Se não, limpa e digita de novo (auto-saves)

---

### 12. Patient ID gera mas texto não aparece no STL
**Causa**:
- (a) Texto retornou null silenciosamente (font não carregou)
- (b) Char com hole (O/D/B) travou manifold
- (c) Texto FORA do cilindro (posicionamento errado)
**Fix**:
- Console: procura `[PSI/Text] font loaded` — se ausente, problema de CDN
- Console: procura `[PSI/Text] "..."` — confirma texto foi gerado
- Console: procura `dumpBbox textID` — confirma bbox razoável (~10×4×1.2mm)
- Se nenhum log aparece: `state.patientId` provavelmente vazio (digita no input)

---

### 13. "Generate PSI failed: All 3 leg positions required"
**Causa**: alguma leg ficou null no state.
**Fix**:
- Reset to auto positions (botão)
- Ou drag manual de cada esfera

---

### 14. Bbox final: `size= 25.2×215.7×200.2 mm` (ou similar absurdo)
**Causa**: cilindros saindo enormes. Provavelmente regressão no `manifoldCylinder`.
**Fix**:
- Procura `dumpBbox` no console — qual primitivo é monstro?
- Confirma `bake-into-vertices` em `manifoldCylinder`
- Hard refresh com `?v=10` (cache)

---

### 15. Tempo de geração > 30 segundos
**Causa**: muitas iterações de mergeVertices na escapula, ou escapula muito grande.
**Fix**:
- Verifica `[PSI/Manifold] Scapula merge tol=...` no console — quantas tentativas?
- Se >1, escapula não estava limpa → rodar MeshLab
- Se escapula >300k tris, considerar decimação prévia

---

### 16. Browser não pega código novo apesar de Cmd+Shift+R
**Causa**: cache stale (raro mas acontece).
**Fix**:
- Abre `?v=N` query string nova
- Network tab DevTools → Disable cache
- Aba anônima (Cmd+Shift+N)
- Confirma marker `[PSI] code build: vN` no console

---

### 17. Texto ID aparece mas em direção errada (esquerda em vez de lateral)
**Causa**: side do paciente é Left, e `glenoidRight` aponta medial.
**Fix conceitual**:
- Comportamento atual: texto sempre na direção de `glenoidRight` projetado
- Para left shoulder, glenoidRight aponta pra **direita do paciente** = MEDIAL nesse caso
- Idealmente: usar direção lateral (oposto, baseado em `state.side`)
- TODO no `buildPatientIDTextManifold`: `if (side === 'L') outDir.negate();`

---

## Quando NADA funciona

1. **Limpa localStorage**: DevTools → Application → Clear site data
2. **Hard refresh**: Cmd+Shift+R + `?v=` query string
3. **Confirma marker**: `[PSI] code build: vN` no console
4. **Verifica arquivos**: `ls -la data/` — todos presentes?
5. **Verifica servidor**: `curl -I http://localhost:8080/test-psi.html`
6. **Última resort**: `git diff test-psi.html` — alguma mudança não-intencional?

Se nada acima resolver: ler `PSI_IMPLEMENTATION.md` §4 "JORNADA DE ERROS" — talvez seja um bug NOVO que não está catalogado ainda. Documenta o caso e adiciona aqui.
