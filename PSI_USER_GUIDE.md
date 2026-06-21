# PSI User Guide — Guia Cirúrgico

**Para**: cirurgião ou planejador que vai USAR a ferramenta PSI.
**Pré-requisito**: caso já passou pelo pipeline (CT → segmentação → `planning_payload.json` + `scapula.obj`).

---

## O que é o PSI

PSI = Patient-Specific Instrument. Um **tripé impresso em 3D** que apoia na rim da glenoide e
guia o **fio de Kirschner** (K-wire Ø2.5mm) exatamente na trajetória planejada para o implante.

Componentes do guia:
- **3 pés cilíndricos** (Ø10×6mm) que apoiam em 3 pontos da rim da glenoide
- **Cilindro central** (Ø10×20mm) que carrega a guia do K-wire
- **3 pernas** conectando cada pé ao cilindro central (forma de tripé)
- **3 esferas fillet** no junção pé↔perna (smooth blend)
- **Furo Ø2.5mm** ao longo do K-wire planejado
- **Patient ID** em relevo na parte superior do cilindro central

---

## Fluxo de uso

### 1. Pré-requisitos (uma vez por caso)

```
data/scapula.obj            ← do pipeline (marching cubes do CT segmentado)
data/planning_payload.json  ← do pipeline (landmarks + axes)
data/scapula_manifold.obj   ← PROCESSAR no MeshLab (ver MESHLAB_PSI_WORKFLOW.md)
```

**MeshLab é OBRIGATÓRIO** se quiser usar o engine manifold-3d (que produz STL imprimível direto).
Sem essa etapa, o engine BVH ainda funciona mas precisa de repair externo.

### 2. Abrir o PSI Prototype

```
http://localhost:8080/test-psi.html
```

Ou na produção: `https://schulterplan.vercel.app/test-psi.html` (quando for deployado).

A página carrega:
- Escapula do paciente em 3D (re-centrada na glenoide)
- Cilindro verde do K-wire trajectory
- 3 esferas coloridas auto-posicionadas a 120° na rim
  - 🔴 Upper (vermelho) — superior
  - 🟢 Middle (verde) — antero-inferior
  - 🔵 Lower (azul) — postero-inferior

### 3. Ajustar a posição das pernas (drag)

**Click e arrasta cada esfera** pra escolher onde quer apoiar o pé do guia.
A esfera SNAPS automaticamente na superfície do osso.

**Regras de validação** (lado direito):
- ✅ **Min spacing ≥ 12mm**: pares de pernas precisam ter espaço entre si
- ✅ **All on glenoid rim region**: nenhuma perna > 35mm do centro
- ✅ **Triangle area > 50 mm²**: triângulo das pernas não pode ser degenerado (alinhado)
- ✅ **Min ≥ 6mm from K-wire**: pernas não podem colidir com o furo do K-wire

Quando alguma falhar, fica vermelha (✗). Reposicione até todas ficarem verdes.

**Atalho**: botão `Reset to auto positions` volta pra config inicial 120°.

### 4. Adicionar Patient ID (opcional)

Campo de texto "Patient ID" na sidebar esquerda:
- Max 10 caracteres
- Aparece em **relevo** na parte superior do cilindro central
- Lê ao longo do eixo do guia, virado pro lado lateral (cirurgião vê quando segura)
- Exemplo: `JD-2026`, `RX1234`, `PT-A99`

Não é obrigatório — se vazio, o guia gera sem texto.

### 5. Selecionar engine

Sidebar esquerda → Engine:

| Engine | Quando usar | Output |
|---|---|---|
| **manifold-3d (WASM, manifold ✓)** | Padrão. Quase sempre. | STL imprimível direto |
| **three-bvh-csg** | Fallback se manifold falhar | STL precisa repair externo |

Se você não fez o MeshLab pre-process, manifold-3d vai pular a subtração óssea
(pés sem concavidade) e logar aviso. Resultado ainda é manifold mas o fit fica
pior.

### 6. Gerar PSI

Clica **Generate PSI**. Aguarda ~3-7 segundos.

HUD esperado (top-left):
```
PSI generated · 4500ms · 13,224 triangles · manifold ✓
```

Se aparecer texto laranja `bone subtract skipped`, você não tem `scapula_manifold.obj`
ou ele não foi cleaned. Volte pro MeshLab.

Se aparecer `14609 open · 3 non-manifold edges` em vermelho, você está no engine
BVH — precisará de repair externo.

### 7. Download STL

Botão **Download STL** (habilitado após gerar).
Arquivo: `scapula_psi_{caseId}_{timestamp}.stl`

### 8. Verificar no MeshMixer / Meshmixer / Bambu Studio / etc

Antes de imprimir, abra no software de slicer:
- Confirma que é manifold (sem buracos)
- Confirma orientação correta
- Adiciona supports se necessário (parte que apoia nos pés precisa estar pra cima)
- Ver `PSI_PRINT_GUIDE.md` (a criar) pra recomendações de print

### 9. (Se BVH) Repair externo

Se gerou com BVH e tem open edges:
- Upload para <https://www.formware.co/onlinestlrepair>
- Ou abra no MeshMixer → Analysis → Inspector → Auto Repair All
- Re-baixa o STL limpo

---

## Cenários típicos

### Cenário A — Tudo perfeito
1. Pipeline pronto
2. MeshLab processado → `scapula_manifold.obj`
3. Ajustar legs, ID, generate
4. STL manifold ✓ direto pro slicer
5. Imprimir, esterilizar, usar

### Cenário B — Sem MeshLab (pressa)
1. Pipeline pronto
2. Selecionar BVH engine
3. Generate → STL com open edges
4. Upload pro formware.co → STL limpo
5. Imprimir

### Cenário C — Caso atípico (glenoide muito pequena ou anatomia complexa)
1. Drag manual cuidadoso das 3 esferas pra evitar áreas finas
2. Verifica `Min spacing ≥ 12mm`
3. Se persistir falha CSG, tentar mover lower leg pra mais distante
4. Reportar ao dev — pode precisar ajuste de parâmetros (PSI.FOOT_DIAMETER)

---

## Limites atuais

- 1 só tipo de PSI: **Tripod simples** (3 pés + cilindro central + furo K-wire)
- Sem sleeve retrátil (template CustomedAI "Tripod With Sleeve" ainda não implementado)
- Sem ajuste de parâmetros via UI (precisa editar `PSI` object no código pra trocar Ø/altura)
- Patient ID flat sobre superfície tangente (não wrapped) — visualmente OK pra 10 chars Ø10mm
- 1 modelo: scapula only. Humerus PSI = roadmap futuro.

---

## Validação clínica (pendente)

- [ ] Imprimir 1 protótipo no caso de teste
- [ ] Verificar fit em phantom impresso da escapula
- [ ] Verificar fit em cadáver (se disponível)
- [ ] Documentar erros de posicionamento (mm) entre planejado vs executado
- [ ] Comparar com CustomedAI no mesmo caso (gold standard)

Ver `PSI_IMPLEMENTATION.md` §8 para roadmap completo.
