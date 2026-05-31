# CustomedAI — PSI Generation Analysis Report
## Análise completa do HAR `app.customed.aiDATAPSI.har` (368MB, 207 entries)

**Caso analisado:** RSA-DEMO (caseId=506), ombro esquerdo
**Usuário:** João Artur Bonadiman (id 83), org "IOT-HSVP"
**PSI gerados:** 1 humeral (Union) + 2 escapulares (Tripod, auto + user)
**Foco do relatório:** PSI da escápula (Tripod glenoide)

---

## 1. RESUMO EM 1 PARÁGRAFO

A geração do PSI **NÃO é feita no browser**. O cliente apenas (a) coleta 3 pontos
no rebordo da glenóide que o usuário pode arrastar e (b) faz upload desses pontos
para a API. Toda a engenharia da peça (legs + corpo + canal do fio K) é executada
por um serviço backend em **~30-60s** que retorna um STL pronto para impressão.
A segmentação CT, a detecção de landmarks anatômicos e o cálculo do eixo
anatômico **também são pré-processados no backend** (`Wand` pipeline) — para o
caso demo eles vêm prontos em ZIPs estáticos no S3. O browser só renderiza,
arrasta esferas e dispara polling. Replicar isso significa replicar o backend
(Python/CGAL/trimesh) — o frontend é fácil.

---

## 2. FLUXO COMPLETO DA SESSÃO (207 requests)

### Tabela cronológica das 5 tasks observadas

| Task | ID    | Service       | Surgery group | Origem    | Duração estimada     |
|------|-------|---------------|---------------|-----------|----------------------|
| 1    | 46009 | surgical_plan | scapula       | auto      | ~10s (2→12→100%)    |
| 2    | 46010 | surgical_plan | humerus       | auto      | ~15s                 |
| 3    | 46011 | **psi**       | humerus       | auto      | ~30s (Union template) |
| 4    | 46012 | **psi**       | **scapula**   | auto      | ~40s (Tripod inicial) |
| 5    | 46013 | **psi**       | **scapula**   | **user**  | ~40s (após mover pernas) |
| 6    | 46014 | export        | scapula       | auto      | ~30s                 |

### Etapas do polling do PSI da escápula (task 46012, auto)
```
  1%  Loading data
 29%  Adding legs
 39%  Adding legs
 49%  Adding legs
 69%  Preparing mesh for print
 79%  Removing kwire from psi
 80%  Saving results
100%  SUCCESS
```

### Etapas do PSI da escápula REGENERADO (task 46013, user)
```
  1%  Loading data
 19%  Aligning anatomies to canonical axis    ← ETAPA EXTRA (auto pulou)
 29%  Adding legs
 49%  Adding legs (×2)
 69%  Preparing mesh for print (×5)
 79%  Removing kwire from psi
100%  SUCCESS
```

A versão user faz mais 1 etapa ("Aligning anatomies to canonical axis") porque
os pontos foram editados — precisa transformar das coordenadas mundiais
para o frame canônico do scapula antes de processar.

### Etapas do PSI do úmero (task 46011, Union template)
```
  1%  Loading data
 49%  Creating legs
 50%  Create lower connecting part           ← VOCABULÁRIO DIFERENTE
 55%  Processing PSI (×4)
 65%  Preparing mesh for print
100%  SUCCESS
```

O úmero usa **2 legs** ("left_leg" e "right_leg"), não 3.

---

## 3. ⭐ O CORE: COMO O PSI É DEFINIDO PELO USUÁRIO

### O input do PSI da escápula são apenas **3 pontos JSON**

Arquivo enviado em `psi_landmarks.zip` (897 bytes):

```
LANDMARKS#psi/scapula_left#POINT#upper_leg.json
LANDMARKS#psi/scapula_left#POINT#middle_leg.json
LANDMARKS#psi/scapula_left#POINT#lower_leg.json
```

Cada um contém:
```json
{
  "coordinates": [133.157, -127.210, 767.022]
}
```

Coordenadas em **mm físicos do NIfTI** (mesmo espaço que o nosso pipeline).

### Comparação auto vs user-edited (mostra que SÓ as coordenadas mudam)

| Ponto       | Auto (task 46012)                         | User-edited (task 46013)                  | Δ (mm) |
|-------------|-------------------------------------------|-------------------------------------------|--------|
| upper_leg   | 120.05, -145.76, 758.31                   | 133.16, -127.21, 767.02                   | ~24 mm |
| middle_leg  | 123.55, -146.86, 738.29                   | 123.65, -147.80, 740.65                   | ~3 mm  |
| lower_leg   | 138.49, -130.42, 729.61                   | 134.93, -138.58, 730.80                   | ~9 mm  |

→ User moveu agressivamente o `upper_leg`, leve no `lower_leg`, quase nada o `middle`.

### PSI do úmero usa 2 pontos com naming bizarro
```
LANDMARKS#psi/scapula#POINT#humerus_left#POINT#left_leg.json
LANDMARKS#psi/scapula#POINT#humerus_left#POINT#right_leg.json
```
(O prefixo `scapula#POINT#humerus_left#POINT#` é redundante — provavelmente
artifact do sistema de naming hierárquico que usam.)

### Como o usuário ARRASTA os pontos (código no ThreejsEditor)
```javascript
createMovingSpheres(e){
  e.forEach(t=>{
    const i=new Mesh(new Sphere(1.5), AT.clone());
    i.name = `${t.name}_modifier_skippedSphere_dont_export`;
    i.position.copy(t.position);
    i.userData = { type:"POINT" };
    const n = new Mesh(new Sphere(2), cT.clone());
    n.name = `${t.name}_outline_modifier_skippedSphere_dont_export`;
    i.attach(n);   // outline contorno
    this.group.attach(i);
    this.spheres.push(i);
  });
}
```

- 1 esfera interna (r=1.5mm) + 1 outline (r=2mm) por leg point
- Sufixo `_modifier_skippedSphere_dont_export` é UM CONVÊNIO de naming:
  - `_modifier` → indica que é arrastável
  - `_skippedSphere` → não conta como landmark anatômico
  - `_dont_export` → não vai pro export final
- Raycaster pega clicks; `onPointSelected(uuid)` ativa drag
- Console logs do Bruno confirmam: `"Hovered object: LANDMARKS#psi/scapula_left#POINT#upper_leg_modifier_skippedSphere_dont_export"` → `"point selected"`
- `OrbitControls.enabled = false` durante drag

### Output do servidor: STL binário simples

```
psi.zip (632 KB)
└── psi/psi.stl    1.4 MB, 28 148 triângulos, header zerado
```

Sem K-wire externos no caso da escápula (eles foram **subtraídos** do corpo na
etapa "Removing kwire from psi" — viram um furo no STL).
O úmero TEM K-wires separados:
```
psi.zip (669 KB)
├── psi/psi.stl              1.5 MB
├── psi/KWIRE_cmkw32_1.stl   5 KB
└── psi/KWIRE_cmkw32_2.stl   5 KB
```

---

## 4. SEGMENTAÇÃO E LANDMARKS — O QUE PROCESSOU O EXAME

### Você perguntou: "qual sistema ele usou para processar?"

**Resposta:** Não dá pra ver porque este é um caso DEMO. Tudo foi pré-cozinhado
no backend e o cliente apenas baixou ZIPs estáticos de S3:

```
GET /api/segmentation/latest/506
  → { preAnatomiesZipPath: "s3://.../demo-cases/RSA/segmentation/segmentation.zip" }
  → contém:
       anatomies_3/MAIN#scapula_left.stl   7.5 MB
       anatomies_3/MAIN#humerus_left.stl   3.2 MB
```

```
GET /api/landmark/latest/506?createdBy=auto&status=approved
  → contém zip de 2.7 MB com:
     - 14 POINT JSONs (Glenoid Center, Trigonum Scapulae, Bicipital Groove, etc.)
     - 8 SURFACE STLs (Glenoid Surface, Humeral Head, Articular, Lesser/Greater Tuberosity)
     - 2 PLANE STLs (Glenoid Plane, Humeral Neck Plane)
     - 1 SPHERE STL (Humeral Head Sphere) ← usado para head_radius
     - Eixos anatômicos pré-calculados como matrizes 4×4 inline no JSON:
         humerus_left: [[a,b,c,d],...]
         scapula_left: [[a,b,c,d],...]
```

### Lista exata de landmarks que o backend produz (≡ "o que eles segmentam")

**Escápula:**
- POINT: Glenoid Center, Trigonum Scapulae, Inferior Angle Of The Scapula,
  Lateral/Medial Supraspinous Floor, Supraspinous Fossa-Glenoid/Medial Intersection
- SURFACE: Glenoid Surface, Supraspinous Floor
- PLANE: Glenoid Plane

**Úmero:**
- POINT: Bicipital Groove Floor/Distal/Proximal, Distal/Proximal Anatomical,
  Greater/Lesser Tuberosity Lateral
- SURFACE: Humeral Head Articular, Bicipital Groove, Anatomical Neck,
  Lesser Tuberosity, Shaft Cortical Surface
- PLANE: Humeral Neck Plane
- SPHERE: Humeral Head Sphere

**Conclusão:** essa lista é praticamente IDÊNTICA ao que nosso pipeline gera.
Eles têm um Glenoid Surface e Supraspinous Floor que nós não temos
formalmente, mas é coisa derivável dos dados que já temos.

### O segmentador real é proprietário
- Bundle JS principal é `index-DkSmr2Kk.js` (2.9MB) — apenas FAZ requests
- O caminho da seg é `demo-cases/RSA/segmentation/segmentation.zip` —
  static asset.
- Para um caso real, deveria existir um endpoint `POST /api/tasks/request/segmentation/{caseId}`
  que dispara o segmentador no backend (não capturado pois caso é demo).
- Console do Bruno mostra `[MedusaDiagnostics:EditorVolume]` mas isso é apenas
  o renderer DICOM (visualização), não o segmentador.

---

## 5. ⭐ ⭐ ENGENHARIA SERVER-SIDE DO PSI (o que o backend faz)

A geração do mesh é 100% server-side. Pelas mensagens do polling, dá pra
deduzir o pipeline em pseudo-código:

```python
def generate_psi_scapula_tripod(case_id, surgery_group, psi_type, user_legs=None):
    # Etapa 1: Loading data (1%)
    scapula_stl = fetch_segmentation(case_id, "scapula_left")
    landmarks = fetch_landmarks(case_id)             # auto + anatomicalAxis
    surgical_plan = fetch_surgical_plan(case_id)     # TEMPLATE_*.glb + transform
    implant_glb = fetch_template(surgical_plan.serial)
    psi_template = lookup_psi_template_by_type(psi_type)  # "Tripod"

    if user_legs:
        # Etapa 1.5: Aligning anatomies to canonical axis (19%)
        # User entregou pontos no mundo CT; trazer para frame canônico
        T = landmarks.anatomicalAxis["scapula_left"]   # matriz 4×4
        legs_canonical = [T_inv @ p for p in user_legs]
    else:
        # Auto-pick 3 pontos no rebordo da glenoide via análise da Glenoid Surface
        legs_canonical = auto_select_tripod_legs(landmarks.glenoid_surface,
                                                  surgical_plan.implant_axis)

    # Etapa 2: Adding legs (29-49%)
    # Para cada ponto leg: criar cilindro/perna sólida que parte do ponto e converge
    # no eixo do K-wire (que vem do surgical_plan = posição do implante)
    legs_mesh = []
    kwire_axis = surgical_plan.implant_axis  # eixo do peg/K-wire
    for leg_point in legs_canonical:
        leg = build_leg_geometry(leg_point, kwire_axis, scapula_stl)
        legs_mesh.append(leg)

    # Etapa 3: Preparing mesh for print (69%)
    # Boolean union de todas as legs + corpo central que segue o rebordo da glenoide
    # Smoothing, manifold-fix, wall thickness mínima
    body = build_glenoid_contact_body(scapula_stl, legs_canonical)
    psi_solid = boolean_union(body, legs_mesh)
    psi_solid = ensure_manifold(psi_solid)
    psi_solid = smooth_for_printing(psi_solid)

    # Etapa 4: Removing kwire from psi (79%)
    # Subtrair canal cilíndrico (~2mm Ø) ao longo do eixo do K-wire
    # Resultado: o fio passa pelo PSI até atingir o osso no ponto planejado
    kwire_cylinder = build_cylinder(kwire_axis, diameter=2.0, length=80)
    psi_solid = boolean_difference(psi_solid, kwire_cylinder)

    # Etapa 5: Saving results (80%)
    upload_to_s3(psi_solid, f"cases/{case_id}/.../psi.zip")
    return psi_solid
```

### Evidência no código de bibliotecas geométricas

Pelo bundle: nada de booleano no cliente. As únicas refs a "kwire" são:
```javascript
const NB = ["kwire","k-wire","psi"];  // tipos de objeto reconhecidos
```
e nomes de arquivo. Confirma: TUDO booleano/manifold é backend.

Stack provavelmente:
- **Python + numpy/numpy-stl** (parsing STL)
- **trimesh** ou **PyMesh** ou **OpenCascade/CGAL** (booleans)
- **Open3D** ou **scipy** (smoothing)
- **manifold3d** (recente, MIT, rapidíssimo — favorito atual da indústria)

Não temos visibilidade dos containers no S3 path, mas pelo cadenced de
~30-40s por mesh, parece **manifold3d ou CGAL** (não algo lento como
Blender BMesh).

### A nota "Removing kwire from psi" é a etapa-chave clínica
Significa: o cilindro do K-wire **vira um furo** no PSI. Quando o cirurgião
encaixa o PSI na glenóide e enfia o fio K, o fio é AUTOMATICAMENTE
direcionado ao ponto planejado de inserção do implante. Esta é a função
fundamental do guide: **transferir o plano virtual para o paciente real
via um único fio guia**.

---

## 6. APIs USADAS — INVENTÁRIO COMPLETO

### CRUD básico
```
GET    /api/auth                                  # login
GET    /api/auth/organizations                    # multi-tenant
GET    /api/case/by-case-number/{caseNumber}      # carregar caso
GET    /api/case/{caseId}                         # carregar caso por id
GET    /api/surgeryType/case/{caseId}             # RSA, TKR, etc.
```

### Dados estáticos pré-computados
```
GET /api/segmentation/latest/{caseId}             # → S3 zip URL
GET /api/landmark/latest/{caseId}?createdBy=auto&status=approved
GET /api/psitype/{caseId}/case                    # tipos disponíveis (Tripod, Union, Minimal)
GET /api/template_library/{caseId}?side=left      # implantes compatíveis
GET /api/template_library/{caseId}/serial/{serialNumber}  # detalhes de 1 implante
```

### Pipeline de tasks assíncronas
```
POST /api/tasks/prepareforcases                   # inicializar
POST /api/tasks/request/surgicalplan/{caseId}     # → { id: 46009 }
POST /api/tasks/request/psi/{caseId}              # → { id: 46011 }   ⭐
POST /api/tasks/request/export/{caseId}           # → { id: 46014 }
GET  /api/tasks/{taskId}                          # polling (500ms cadence)
```

### Upload de pontos editados pelo user (multipart S3)
```
GET  /api/fileUpload/init_upload/case/{caseId}/{type}?version=...&surgeryGroup=...
        # type ∈ { landmarks, psi_landmarks, surgical_plan }
        # → { uploadId, key, bucket }
PUT  /api/fileUpload/upload/multipart/part        # body: { filePath, uploadId, partNumber }
                                                  # → presigned S3 URL
PUT  https://prod-customedai-storage.s3.eu-west-1.amazonaws.com/...  # upload do ZIP
PUT  /api/fileUpload/upload/multipart/complete    # body: { filePath, uploadId, parts:[{ETag,PartNumber}] }
```

### Persistência de versões aprovadas
```
POST /api/landmark/new/{caseId}                   # cria registro apontando para o zip
POST /api/landmark/{id}/approve                   # marca como user-approved
POST /api/surgicalplan/new/{caseId}               # idem para surgicalplan
POST /api/surgicalplan/{id}/approve
DELETE /api/surgicalplan/cases/{caseId}?surgeryGroup=...&excludeEntityId=...  # invalida outros
DELETE /api/psi/cases/{caseId}?surgeryGroup=...
DELETE /api/export/cases/{caseId}?surgeryGroup=...
```

### Resultados
```
GET  /api/psi/latest/{caseId}?version=...&surgeryGroup=scapula
        # → { psiFolderPath: "s3://.../psi_design/user_scapula_{version}" }
POST /api/fileUpload/list                         # lista arquivos no folder
POST /api/fileUpload/{userId}/download            # gera presigned URL pra cada
GET  https://prod-cdn.customed.ai/.../psi.zip     # download STL
GET  /api/export/latest/{caseId}?surgeryGroup=...
```

---

## 7. SISTEMA DE NAMING — DECODIFICADO

Eles usam **separators hierárquicos com `#`** dentro de nomes Three.js:
```
LANDMARKS#psi/scapula_left#POINT#upper_leg.json
└──┬──┘ └┬┘└────┬────┘ └─┬─┘ └──┬──┘
   │     │      │        │       │
   group context anatomy type    name
```

Tipos reconhecidos no bundle:
```javascript
const NB = ["kwire","k-wire","psi"];                     // export categories
const groupTypes = { PRE_ANATOMIES, LANDMARKS, PSI, PSI_LANDMARKS, SURGICAL_TOOLS };
const landmarkTypes = ["POINT","SURFACE","PLANE","SPHERE"];
```

Sufixos especiais (rules in JS):
- `_modifier_skippedSphere_dont_export` → arrastável, não vai pro export
- `_outline_modifier_skippedSphere_dont_export` → outline da esfera

Quando o usuário arrasta `upper_leg_modifier_skippedSphere`, o sistema
atualiza a `position` daquela esfera (em mm físicos do NIfTI) e
zipa todas as posições em JSONs com prefixo `LANDMARKS#psi/`.

---

## 8. TEMPLATES DE PSI DISPONÍVEIS (do `/api/psitype/506/case`)

| ID | Name | Group | Subtitle | Descrição |
|----|------|-------|----------|-----------|
| 1  | **Tripod** | scapula | Glenoid Surgical Guide | "Three adjustable legs position securely around the glenoid for optimal exposure, providing precise K-wire guidance to the planned entry point and angle." |
| 2  | **Tripod With Sleeve** | scapula | Glenoid Surgical Guide | "Retractable sleeve allows a two-step placement. Initial positioning for visibility, then guided K-wire insertion with precision and control." |
| 11 | **Minimal** | humerus | Humeral Surgical Guide | "Compact, low-profile guide with a precision shelf directing the blade accurately to the planned site and angle, minimizing exposure with two adjustable legs." |
| 15 | **Union** | humerus | Humeral Surgical Guide | "Stable, minimal-footprint guide with a defined contact surface and precision shelf for accurate blade alignment and controlled exposure." |

→ Para escápula são **dois templates** (Tripod = 3 pernas com furo K-wire, ou
Tripod with Sleeve = mesma estrutura + manga retrátil).
→ Sleeve = peça plástica extra que evita o fio entortar até cair na glenóide.

---

## 9. ESTADO DA ARTE — O QUE NÓS PODEMOS REPLICAR

### ✅ FÁCIL (frontend só) — 1-2 semanas
| Capacidade | Como |
|------------|------|
| 3 esferas arrastáveis no rebordo da glenóide | Three.js raycaster + `OrbitControls.enabled=false` durante drag (igual nosso lasso). Já temos isso! |
| Validação dos pontos (no rebordo, espaçamento mínimo, dentro da Glenoid Surface) | Checagem geométrica simples |
| Auto-placement inicial das 3 pernas | Sample circular ao redor do `glenoid_center` no plano da glenóide |
| Upload do ZIP de JSONs | Igual nosso fluxo (substituir pelo S3 deles seria trivial) |
| Visualização do STL retornado | Mesma rotina de loader que já temos |
| K-wire como cilindro (visualização) | Cilindro de 2mm Ø ao longo do `friedmanAxis` × 80mm |

### 🟡 MÉDIO (backend Python) — 4-6 semanas
| Capacidade | Como |
|------------|------|
| **Geração do mesh PSI no servidor** | Python + manifold3d para booleans + trimesh para load/save |
| Construção das pernas (cilindros tangentes que convergem no eixo K-wire) | Geometria de cone truncado, raio variável |
| Corpo central que conforma ao rebordo da glenóide | Boolean intersect entre uma esfera deslocada do glenoid_center e o offset do scapula_stl |
| Subtração do canal do K-wire (2mm Ø) | `boolean_difference(psi_body, cylinder)` |
| Smoothing + wall thickness mínima | trimesh.smoothing + offset |

### 🔴 DIFÍCIL (precisaria ML pipeline) — meses, não dias
| Capacidade | Como |
|------------|------|
| **Segmentação automática CT → STL** | nnUNet ou outro modelo pré-treinado para escápula/úmero. Existe `MONAI` aberto, mas treinar requer dataset anotado |
| **Detecção automática de landmarks** | Modelo de coordinate regression treinado em scans rotulados. Open-source raro nessa anatomia específica |
| **Eixo anatômico canônico** | PCA + heurísticas dos landmarks. Achievable se você confiar nos landmarks |

### ⚪ NÃO PRECISA replicar
- "Medusa" volume renderer (proprietário) — nós usamos NiiVue
- Multi-tenant / billing / Intercom — fora de escopo

---

## 10. ⭐ PLANO DE IMPLEMENTAÇÃO MÍNIMO — PSI DA ESCÁPULA

### Fase A — Frontend (interativo, sem geração de mesh ainda)
1. Adicionar 3 esferas (r=1.5mm) no rebordo da glenóide ao redor do `glenoid_center`
2. Posicionamento inicial: 3 pontos a 120° no plano da glenóide, raio 12-15mm
3. Tornar arrastáveis com raycaster (já temos infra do measure tool)
4. **Snap to surface** durante drag: raycast contra o `scapulaMesh` para que o ponto fique colado no osso
5. Visualizar K-wire trajectory: cilindro verde de 2mm Ø ao longo do `friedmanAxis` (eixo do peg do implante), comprimento 80mm
6. Persistir os 3 pontos em localStorage com a mesma estratégia que usamos pro lasso

### Fase B — Backend stub (visualizar resultado simulado)
1. Endpoint `POST /api/psi/generate` (FastAPI ou Express)
2. Recebe `{ legs: [...], scapulaStl, implantAxis }`
3. Por enquanto, retorna um STL placeholder (cilindro union 3 esferas)
4. Frontend mostra o STL retornado por cima da glenóide

### Fase C — Backend real (a parte cara)
1. Python service usando **manifold3d** (https://github.com/elalish/manifold)
2. Pipeline:
   - Build leg cylinders (tangentes às esferas, convergem no eixo)
   - Build body como offset do contorno glenoidal
   - Union de tudo
   - Subtract cilindro K-wire de 2mm
   - Export STL binário
3. Tempo alvo: <30s
4. Eventualmente: docker container atrás de fila (Redis/celery) com polling igual o CustomedAI

### Fase D — Apresentação para impressão
1. Botão "Download PSI" → ZIP com:
   - `psi.stl` (corpo principal)
   - `report.pdf` (gerado por puppeteer com screenshots + medidas)
2. Slicer-ready (já em mm, manifold, manifold-checked)

---

## 11. RED FLAGS / OBSERVAÇÕES TÉCNICAS

1. **Datas no HAR estão em 2026** — relógio do cliente bagunçado ou timestamp do servidor. Não afeta a análise mas é curioso.
2. **Os ZIPs de PSI são DOWNLOADED 2x** (entries 40-41 e 43-44 são duplicados do RSA.zip DICOM) — provavelmente o React faz 2 fetches por mounting do EditorWrapper ou o Range request foi reiniciado.
3. **Surgical plan TEMPLATE_1050024.glb tem 34MB descomprimido** (11MB zipado) — é o GLB do implante Agilon escapular completo com texturas. Pra nós não precisamos disso (já temos STLs).
4. **A coordenada Z dos legs é ~730-770** — bate com `glenoid_center.z = 750.31`. Confirma que os legs estão concentrados em um anel de ±20mm em Z em torno do centro da glenóide, no plano da face glenoidal.
5. **`anatomicalAxis` na resposta é uma matriz 4×4 row-major** — coluna 4 é translação (mm). Mesmo padrão do nosso pipeline.

---

## 12. CONCLUSÃO EXECUTIVA

| Pergunta sua                                          | Resposta                                                                                       |
|-------------------------------------------------------|------------------------------------------------------------------------------------------------|
| **Qual sistema de segmentação usaram?**               | Proprietário, server-side. Não-visível no HAR (caso é demo com STL pré-cozinhado).             |
| **Como identificam landmarks?**                        | Server-side. Retorna ZIP com 14 POINT JSONs + 8 SURFACE STLs + 3 PLANE/SPHERE STLs.            |
| **Quanto tempo demora o processamento?**               | Não capturado para auto (caso demo). Para PSI manual: ~30-40s, polling 500ms.                 |
| **Como o PSI é gerado?**                              | Backend recebe 3 JSONs com `{coordinates}` + scapula STL + surgical plan, faz boolean union + difference, retorna STL binário. |
| **Replicável?**                                        | **Frontend SIM** (1-2 sem). **Backend mesh SIM** com manifold3d (1-2 meses). **Segmentação NÃO** sem ML pipeline. |
| **Quais templates de PSI escapular existem?**          | 2: "Tripod" e "Tripod With Sleeve" (manga retrátil).                                          |
| **Quantos pontos define um PSI?**                      | Escápula: 3 (upper, middle, lower leg). Úmero: 2 (left_leg, right_leg).                       |
| **O fio K-wire fica visível no STL?**                  | **NÃO no escapular** — é subtraído como furo. **SIM no humeral** — vem como STL separado.    |
| **Coordenadas estão em qual frame?**                   | NIfTI physical mm (igual nosso `xyz_mm`).                                                      |

### Recomendação
Começar pela **Fase A** (3 pontos arrastáveis + visualização K-wire) usando o
caso de teste atual. Em paralelo, pesquisar **manifold3d** e prototipar um
gerador Python local. O STL gerado pode ser visualizado pelo nosso loader
já existente. **O frontend é facilmente replicável; o backend Python é onde
está o valor de engenharia.**

---

*Relatório gerado em 2026-05-29 a partir do HAR `app.customed.aiDATAPSI.har` (368 MB, 207 entries). Caso analisado: RSA-DEMO (Implantcast Agilon, esquerdo). Para o relatório de MPR, ver `MPR_HAR_ANALYSIS_REPORT.md`.*
