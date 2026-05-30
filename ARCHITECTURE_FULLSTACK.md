# SchulterPlan — Arquitetura Full Stack
## Pipeline DICOM → Segmentação → Planejamento 3D + MPR

**Versão**: 1.0  
**Data**: Maio 2026  
**Status**: Proposta de Arquitetura (Pipeline de Segmentação já desenvolvido)

---

## Visão Geral

O sistema é composto por **dois subsistemas separados** que se comunicam via Object Storage:

- **Sistema A** — Processamento pesado (segmentação AI + conversão NIfTI)
- **Sistema B** — Planejamento cirúrgico (SchulterPlan, atual, no Vercel)

A separação é necessária pois tomografias chegam com **~600 MB** (DICOM),
volume impraticável para streaming direto ao browser.

```
CT Scanner / PACS
      │ DICOM (~600 MB)
      ▼
┌─────────────────┐        ┌───────────────────────────────┐
│  Sistema A      │─ S3 ──▶│  Sistema B (SchulterPlan)     │
│  Processamento  │        │  Frontend / Vercel            │
│  + Segmentação  │        │  MPR via NIfTI + 3D Three.js  │
└─────────────────┘        └───────────────────────────────┘
```

---

## Diagrama de Arquitetura Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│  ORIGEM DOS DADOS                                                   │
│                                                                     │
│  PACS / CT Scanner / Upload Web                                    │
│  Output: DICOM Series (~600 MB, múltiplos arquivos .dcm)           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Upload DICOM
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SISTEMA A — Servidor de Processamento (GPU)                       │
│  Stack: Python + FastAPI + GPU (AWS EC2 g4dn ou RunPod)            │
│                                                                     │
│  Etapa 1: SEGMENTAÇÃO AI (pipeline já desenvolvido)                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Input: DICOM Series                                         │  │
│  │  Output:                                                     │  │
│  │    ├─ scapula.obj        (~2 MB)                             │  │
│  │    ├─ humerus.obj        (~12 MB)                            │  │
│  │    └─ landmarks.json     (<1 KB) — pontos anatômicos        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Etapa 2: CONVERSÃO NIfTI (SimpleITK / dcm2niix)                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Input: DICOM Series                                         │  │
│  │  Output:                                                     │  │
│  │    ├─ volume.nii.gz     (~50-150 MB, volume CT completo)     │  │
│  │    │   ├─ Contém header: voxel spacing, orientation matrix   │  │
│  │    │   ├─ Coordenadas RAS/LPS alinhadas com os OBJs          │  │
│  │    │   └─ Volume 3D acessível por slice via Range Requests   │  │
│  │    └─ volume_meta.json  (<1 KB)                              │  │
│  │        ├─ dimensions: [512, 512, 400]                        │  │
│  │        ├─ voxelSpacing: [0.5, 0.5, 0.6] mm                  │  │
│  │        ├─ orientation: matrix 4x4 (RAS)                      │  │
│  │        └─ origin: [x, y, z] mm                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Etapa 3: UPLOAD PARA OBJECT STORAGE                               │
│  └─ Todos os outputs → S3 / GCS → notifica API                    │
│                                                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Upload via SDK (boto3/google-cloud)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  OBJECT STORAGE — AWS S3 (região sa-east-1, São Paulo)             │
│                                                                     │
│  Estrutura de Pastas:                                              │
│                                                                     │
│  cases/                                                            │
│    └─ {caseId}/                    (ex: 2026-05-miria-oe-gps)     │
│         ├─ dicom/                  ← PRIVADO, sem URL pública     │
│         │    └─ *.dcm             (original ~600 MB, backup)      │
│         │                                                          │
│         ├─ models/                                                │
│         │    ├─ scapula.obj        (~2 MB)                        │
│         │    ├─ humerus.obj        (~12 MB)                       │
│         │    ├─ landmarks.json     (<1 KB)                        │
│         │    └─ planning.json      (<1 KB, estado do planejador)  │
│         │                                                          │
│         └─ imaging/                                               │
│              ├─ volume.nii.gz      (~50-150 MB)                   │
│              └─ volume_meta.json   (<1 KB)                        │
│                                                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ URLs Presigned (expiram em 2h)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BACKEND API — Servidor Leve                                       │
│  Stack: FastAPI (Python) + PostgreSQL (Supabase)                   │
│  Host: Render / Railway / AWS Lambda                               │
│                                                                     │
│  Responsabilidades:                                                │
│  ├─ Autenticação e autorização (JWT)                              │
│  ├─ CRUD de casos (criar, listar, atualizar status)               │
│  ├─ Gerar URLs Presigned do S3 (expiração curta, 2h)             │
│  ├─ Notificar médico quando caso está pronto (email/push)         │
│  ├─ Salvar/recuperar cenários de planejamento                     │
│  └─ Audit log (quem acessou qual caso e quando)                   │
│                                                                     │
│  Endpoints:                                                        │
│  POST /cases                  → Criar novo caso                   │
│  GET  /cases/{id}/assets      → Retorna URLs presigned             │
│  PUT  /cases/{id}/planning    → Salvar estado do planejamento     │
│  GET  /cases/{id}/nifti-range → Streaming de slice específico     │
│                                                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ REST API + URLs Presigned
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SISTEMA B — SchulterPlan (Frontend)                               │
│  Host: Vercel (atual, sem mudança)                                 │
│  Stack: Vanilla JS + Three.js r160 + NiiVue.js                    │
│                                                                     │
│  Carregamento de Assets:                                           │
│  ├─ scapula.obj + humerus.obj  → Three.js OBJLoader               │
│  ├─ landmarks.json             → JSON.parse (instantâneo)          │
│  ├─ volume.nii.gz              → NiiVue / nifti-reader-js          │
│  │    └─ HTTP Range Requests   → Só baixa o slice necessário      │
│  └─ planning.json              → Estado salvo do planejamento     │
│                                                                     │
│  Componentes de UI:                                                │
│  ├─ Planejador 3D (test-heroui.html)  — atual                     │
│  ├─ MPR Viewer (novo)                 — NIfTI no browser          │
│  ├─ Planejador do Úmero (humerus.html)— atual                     │
│  └─ Surgery Dashboard                 — atual                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Por Que NIfTI (e Não JPEG Tiles)

### O Problema com JPEG

JPEG tiles perdem informação espacial crítica:
- **Sem localização geográfica**: cada tile é uma imagem "solta" sem coordenadas
- **Sem voxel spacing**: não sabe o tamanho real de cada pixel em mm
- **Sem orientation matrix**: não sabe como o volume está orientado no espaço
- **Sincronização impossível**: não dá para alinhar o corte MPR com a posição do implante 3D

### A Vantagem do NIfTI

```
NIfTI (volume.nii.gz) contém:
│
├─ Header (348 bytes)
│    ├─ dim[]:        dimensões do volume [512, 512, 400]
│    ├─ pixdim[]:     voxel spacing [0.5, 0.5, 0.6] mm
│    ├─ qform_code:   sistema de coordenadas (RAS/LPS)
│    ├─ srow_x/y/z:   matrix de orientação 4x4
│    └─ scl_slope:    escala de intensidade (Hounsfield units)
│
└─ Data (volume 3D completo, acessível por offset de bytes)
     ├─ Slice axial 0:   bytes [offset_0 ... offset_0 + slice_size]
     ├─ Slice axial 1:   bytes [offset_1 ... offset_1 + slice_size]
     └─ ...
```

O NIfTI compartilha o **mesmo espaço de coordenadas** que os OBJ gerados
pela segmentação, tornando a sincronização 3D ↔ MPR direta e precisa.

---

## Visualização NIfTI no Browser

### Bibliotecas Disponíveis

#### Opção Recomendada: NiiVue.js
```
Site:    https://niivue.github.io/niivue/
GitHub:  https://github.com/niivue/niivue
Tipo:    WebGL2-based, suporte nativo a NIfTI
Recursos:
  ├─ MPR automático (axial + coronal + sagittal)
  ├─ Suporte a .nii e .nii.gz
  ├─ Streaming via HTTP Range Requests
  ├─ Controle de window/level (Hounsfield)
  ├─ Overlay de meshes (OBJ/STL sobre o volume)
  └─ Coordenadas em mm (RAS) — sincroniza com Three.js
```

#### Alternativa: nifti-reader-js + canvas 2D manual
```
Site:    https://github.com/rii-mango/NIFTI-Reader-JS
Tipo:    Parser JavaScript puro, sem renderização
Uso:     Lê o NIfTI e você implementa a renderização
Vantagem: Controle total sobre a integração com Three.js
```

### Integração Básica com NiiVue

```html
<!-- Importar NiiVue via CDN -->
<script src="https://cdn.jsdelivr.net/npm/@niivue/niivue/dist/niivue.umd.js"></script>

<canvas id="mprCanvas"></canvas>

<script>
async function initMPR(niftiUrl) {
  const nv = new Niivue({
    show3Dcrosshair: true,   // Cursor 3D sincronizado
    crosshairColor: [1, 0.5, 0, 1],  // Laranja (cor Implantcast)
    backColor: [0, 0, 0, 1], // Fundo preto (tema dark)
  });

  await nv.attachToCanvas(document.getElementById('mprCanvas'));

  // Carrega NIfTI diretamente da URL Presigned do S3
  // NiiVue usa HTTP Range Requests internamente — não baixa tudo
  await nv.loadVolumes([{
    url: niftiUrl,   // URL presigned do S3
    colormap: 'gray',
    opacity: 1
  }]);

  // Listener: quando usuário clica no MPR, recebe coordenadas em mm (RAS)
  nv.onLocationChange = (location) => {
    const { mm } = location;  // [x, y, z] em mm no espaço RAS
    syncImplantWithMPR(mm);   // Sincroniza com Three.js
  };
}
</script>
```

### Sincronização MPR ↔ Three.js 3D

Esta é a funcionalidade mais poderosa: **clicar no MPR move o cursor 3D** e vice-versa.

```javascript
// ─── Sistema de coordenadas compartilhado ───
//
// NIfTI usa: coordenadas RAS em mm (Right-Anterior-Superior)
// Three.js usa: coordenadas do OBJ (geradas pela mesma segmentação)
// Ambos têm ORIGEM e ESCALA idênticas — sincronização direta!

// Quando usuário move crosshair no MPR:
nv.onLocationChange = (location) => {
  const [x, y, z] = location.mm;  // em mm, espaço RAS

  // Posicionar cursor 3D no Three.js
  mprCursorSphere.position.set(x, y, z);

  // Atualizar planos de corte visíveis no 3D viewer
  updateMPRPlanes(x, y, z);
};

// Quando usuário move o implante no 3D:
function updateImplantPose() {
  // ...lógica existente de posicionamento do implante...

  // Sincronizar posição do crosshair no MPR
  const implantCenter = new THREE.Vector3();
  implantMesh.getWorldPosition(implantCenter);

  nv.scene.crosshairPos = nv.mm2frac([
    implantCenter.x,
    implantCenter.y,
    implantCenter.z
  ]);
  nv.drawScene();
}

// Planos de corte MPR visíveis no 3D (opcional - mais imersivo)
function updateMPRPlanes(x, y, z) {
  axialPlane.position.y    = y;
  coronalPlane.position.z  = z;
  sagittalPlane.position.x = x;

  // Atualizar texturas dos planos com o slice correto
  loadSliceTexture('axial',    y);
  loadSliceTexture('coronal',  z);
  loadSliceTexture('sagittal', x);
}
```

---

## HTTP Range Requests — Streaming por Slice

O NIfTI é um arquivo binário com estrutura regular:
**cada slice axial ocupa o mesmo número de bytes** e está em posição previsível.

```
volume.nii.gz (descomprimido: volume.nii)
│
├─ Header NIfTI:  352 bytes (fixo)
│
└─ Dados (float32 ou int16):
     Slice 0: bytes [352 ... 352 + W*H*dtype_size]
     Slice 1: bytes [352 + W*H*dtype_size ... 352 + 2*W*H*dtype_size]
     Slice n: bytes [352 + n*W*H*dtype_size ... ]
```

```javascript
// Calcula o byte range de um slice específico e faz fetch parcial
async function fetchNiftiSlice(niftiUrl, sliceIndex, header) {
  const { dimX, dimY, dtype } = header;  // do volume_meta.json
  const bytesPerVoxel = dtype === 'int16' ? 2 : 4;  // int16 ou float32
  const sliceBytes    = dimX * dimY * bytesPerVoxel;
  const headerOffset  = 352;

  const start = headerOffset + sliceIndex * sliceBytes;
  const end   = start + sliceBytes - 1;

  const response = await fetch(niftiUrl, {
    headers: { 'Range': `bytes=${start}-${end}` }  // HTTP 206 Partial Content
  });

  const buffer = await response.arrayBuffer();
  const pixels = new Int16Array(buffer);  // ou Float32Array

  return pixels;  // 512×512 = 262,144 pixels — ~512 KB apenas
}
```

> **Resultado**: em vez de baixar 150 MB, cada slice busca ~512 KB.
> Latência de ~100-300ms por slice no S3 (excelente para UX).

---

## Formato dos Dados de Saída do Pipeline

### volume_meta.json (gerado pelo Sistema A junto com o NIfTI)

```json
{
  "caseId": "2026-05-miria-oe-gps",
  "patientSide": "left",
  "generated": "2026-05-26T14:30:00Z",

  "volume": {
    "file": "volume.nii.gz",
    "dimensions": [512, 512, 350],
    "voxelSpacingMm": [0.468, 0.468, 0.600],
    "dtype": "int16",
    "valueRange": [-1024, 3071],
    "coordinateSystem": "RAS"
  },

  "orientationMatrix": [
    [ 0.468,  0.0,   0.0,  -119.9 ],
    [  0.0,   0.468, 0.0,  -119.9 ],
    [  0.0,   0.0,   0.6,  -103.8 ],
    [  0.0,   0.0,   0.0,     1.0 ]
  ],

  "anatomy": {
    "glenoidCenterMm": [12.3, -5.6, 88.2],
    "humeralHeadCenterMm": [18.7, 22.1, 115.4]
  }
}
```

### landmarks.json (gerado pelo pipeline de segmentação)

```json
{
  "caseId": "2026-05-miria-oe-gps",
  "side": "left",
  "coordinateSystem": "RAS",

  "scapula": {
    "glenoidCenter":    [12.3, -5.6, 88.2],
    "glenoidNormal":    [0.05, -0.98, 0.19],
    "glenoidUp":        [0.02,  0.19, 0.98],
    "glenoidRight":     [0.99,  0.02, -0.01],
    "inferiorRim":      [12.1, -22.3, 78.5],
    "anteriorRim":      [22.8,  -5.3, 89.1],
    "posteriorRim":     [-0.2,  -5.9, 87.3]
  },

  "humerus": {
    "headCenter":       [18.7, 22.1, 115.4],
    "headRadius":       22.1,
    "longAxisDirection":[0.0, 0.0, -1.0],
    "neckShaftAngle":   136.4
  },

  "preop": {
    "retroversion":     23.0,
    "inferiorInclination": 5.0,
    "subluxation":      0.78
  }
}
```

---

## Fluxo Detalhado de Dados

### Fase 1 — Ingestão e Processamento

```
1. Médico / técnico faz upload do DICOM
   └─ Via web form ou integração PACS (HL7/DICOM network)

2. Sistema A recebe o DICOM
   ├─ Salva original em S3: cases/{id}/dicom/ (backup, acesso restrito)
   └─ Inicia pipeline de processamento

3. Pipeline de Segmentação (já desenvolvido)
   ├─ Input:  DICOM Series (~600 MB)
   ├─ Output: scapula.obj + humerus.obj + landmarks.json
   └─ Upload para: cases/{id}/models/

4. Conversão NIfTI
   ├─ Ferramenta: dcm2niix ou SimpleITK
   ├─ Input:  DICOM Series
   ├─ Output: volume.nii.gz (~50-150 MB)
   └─ Upload para: cases/{id}/imaging/

5. API Backend marca caso como status: "ready"
   └─ Envia notificação para o médico (email / push)
```

### Fase 2 — Abertura do Caso no Planejador

```
6. Médico abre SchulterPlan (Vercel)
   └─ Autentica com JWT

7. Frontend requisita: GET /api/cases/{id}/assets
   └─ API retorna URLs Presigned (válidas por 2h):
        {
          "scapulaUrl":   "https://s3.amazonaws.com/...?X-Amz-Signature=...",
          "humerusUrl":   "https://s3.amazonaws.com/...?X-Amz-Signature=...",
          "landmarksUrl": "https://s3.amazonaws.com/...?X-Amz-Signature=...",
          "niftiUrl":     "https://s3.amazonaws.com/...?X-Amz-Signature=...",
          "metaUrl":      "https://s3.amazonaws.com/...?X-Amz-Signature=..."
        }

8. Frontend carrega assets:
   ├─ scapula.obj + humerus.obj  → Three.js (download completo, ~14 MB)
   ├─ landmarks.json + volume_meta.json → JSON.parse (instantâneo)
   └─ volume.nii.gz              → NiiVue inicia lazy streaming
        └─ HTTP Range Requests: só busca o slice axial visível (~512 KB)
```

### Fase 3 — Uso do Planejador

```
9. Médico planeja no 3D (igual ao estado atual)
   ├─ Ajusta retroversão, inclinação, profundidade
   ├─ Usa Cut Views (axial/coronal/sagittal)
   └─ Implante se move em tempo real

10. Médico ativa o MPR Viewer
    ├─ NiiVue renderiza os 3 planos (axial, coronal, sagittal)
    ├─ Crosshair está centrado no implante
    ├─ Mover crosshair no MPR → cursor se move no 3D
    └─ Mover implante no 3D → crosshair se move no MPR

11. Médico grava comentários por voz
    └─ Persiste em localStorage (ou API futuramente)

12. Médico salva planejamento
    └─ PUT /api/cases/{id}/planning → salva no banco
```

---

## Infraestrutura e Custos Estimados

### Componentes e Hospedagem

```
┌──────────────────────┬─────────────────────────┬────────────────┐
│ Componente           │ Hospedagem               │ Custo/mês      │
├──────────────────────┼─────────────────────────┼────────────────┤
│ Frontend             │ Vercel (atual)           │ $0 – $20       │
│ SchulterPlan         │ Sem mudança necessária   │                │
├──────────────────────┼─────────────────────────┼────────────────┤
│ API Backend          │ Render / Railway         │ $10 – $50      │
│ (FastAPI + Postgres) │ ou AWS Lambda + RDS      │                │
├──────────────────────┼─────────────────────────┼────────────────┤
│ Processamento AI     │ AWS EC2 g4dn.xlarge      │ ~$0.50/hr      │
│ Segmentação          │ ou RunPod / Modal.com    │ (sob demanda)  │
│                      │ Rodar apenas ao receber  │ ~$50-200/mês   │
│                      │ novo caso                │ (estimativa)   │
├──────────────────────┼─────────────────────────┼────────────────┤
│ Object Storage       │ AWS S3 (sa-east-1)       │ ~$5 – $30      │
│ DICOM + OBJ + NIfTI  │ 1 TB = ~$23/mês          │ por volume     │
├──────────────────────┼─────────────────────────┼────────────────┤
│ Banco de Dados       │ Supabase Free / Pro      │ $0 – $25       │
│ Casos, usuários      │ (PostgreSQL gerenciado)  │                │
└──────────────────────┴─────────────────────────┴────────────────┘

TOTAL ESTIMADO: ~$70 – $350/mês dependendo do volume de casos
```

### Estratégia de Custo para GPU

A segmentação não precisa de GPU rodando 24/7:

```python
# Opção A: AWS Lambda + ECS (spin-up sob demanda)
# Quando novo DICOM chega → inicia container GPU → processa → desliga

# Opção B: Modal.com (mais simples para Python AI)
import modal

@modal.function(gpu="T4", timeout=600)
def segment_ct(dicom_path: str) -> dict:
    # Seu pipeline de segmentação aqui
    scapula_mesh = segment_scapula(dicom_path)
    humerus_mesh = segment_humerus(dicom_path)
    landmarks    = extract_landmarks(scapula_mesh, humerus_mesh)
    nifti_volume = convert_to_nifti(dicom_path)

    return upload_to_s3(case_id, scapula_mesh, humerus_mesh,
                        landmarks, nifti_volume)
```

---

## LGPD e Segurança

### Requisitos para Dados Médicos no Brasil

```
1. LOCALIZAÇÃO DOS DADOS
   └─ AWS S3 região sa-east-1 (São Paulo)
       → Dados ficam em território brasileiro (LGPD Art. 33)

2. CRIPTOGRAFIA
   ├─ Em trânsito: HTTPS/TLS 1.3 (obrigatório no S3)
   └─ Em repouso: S3 SSE-S3 ou SSE-KMS (AES-256)

3. CONTROLE DE ACESSO
   ├─ URLs Presigned com expiração curta (2 horas)
   ├─ IAM roles com least-privilege
   ├─ Bucket S3 DICOM: privado, sem URL pública nunca
   └─ Médico só acessa casos do próprio serviço/paciente

4. AUDIT LOG
   ├─ AWS CloudTrail: log de todos os acessos S3
   ├─ API log: quem acessou qual caso e quando
   └─ Retenção mínima: 5 anos (CFM)

5. CONSENTIMENTO
   └─ Termo de uso com finalidade de uso dos dados
       (planejamento cirúrgico, sem comercialização)
```

---

## Roadmap de Implementação

### Fase 1 — MVP sem Mudança no Frontend (1-2 semanas)
```
✅ Manter SchulterPlan no Vercel como está
✅ Criar bucket S3 na região São Paulo
✅ Script de upload manual: OBJ + JSON → S3
✅ Carregar assets via URL direta (sem API ainda)
✅ Validar que OBJ carregado do S3 funciona no Three.js
```

### Fase 2 — API Backend (2-4 semanas)
```
✅ FastAPI com endpoint de casos
✅ PostgreSQL (Supabase) para metadados
✅ Geração de URLs Presigned (expiração 2h)
✅ Autenticação básica (JWT)
✅ Frontend SchulterPlan consome API para buscar URLs
```

### Fase 3 — NIfTI + MPR Viewer (4-8 semanas)
```
✅ Integrar NiiVue.js no SchulterPlan
✅ Painel MPR ao lado do 3D viewer (ou aba separada)
✅ HTTP Range Requests para lazy loading de slices
✅ Sincronização básica MPR ↔ 3D (crosshair)
✅ volume_meta.json gerado pelo pipeline de segmentação
```

### Fase 4 — Sincronização Total (8-12 semanas)
```
✅ Sincronização bidirecional: mover implante ↔ mover crosshair MPR
✅ Overlay do implante sobre o MPR (NiiVue suporta meshes)
✅ Window/level ajustável (Hounsfield: osso, tecido mole, etc.)
✅ Cut views 3D alinhados com planos MPR
✅ Salvar estado completo do planejamento na API
```

### Fase 5 — Produção Clínica (3-6 meses)
```
✅ Upload DICOM via web (drag & drop ou integração PACS)
✅ Pipeline automatizado (DICOM → segmentação → NIfTI → notify)
✅ Multi-usuário e multi-serviço
✅ Relatório PDF com snapshots 3D + MPR + medidas
✅ Conformidade LGPD + auditoria completa
```

---

## Tecnologias Recomendadas

```
Conversão DICOM → NIfTI:
  ├─ dcm2niix (CLI, rápido, padrão em pesquisa médica)
  └─ SimpleITK (Python, mais controle)

Leitura NIfTI no Browser:
  ├─ NiiVue.js (recomendado — WebGL2, MPR pronto)
  └─ nifti-reader-js (parser puro, mais controle)

API Backend:
  └─ FastAPI (Python — mantém mesma linguagem do pipeline AI)

Banco de Dados:
  └─ Supabase (PostgreSQL + Auth + Storage, tudo em um)

Object Storage:
  └─ AWS S3 (sa-east-1) — padrão da indústria médica

Processamento Sob Demanda:
  ├─ Modal.com (mais simples para Python AI)
  └─ AWS EC2 g4dn.xlarge (mais controle, mais barato em escala)
```

---

## O Que Não Muda

```
✅ SchulterPlan continua no Vercel
✅ Toda a lógica de planejamento atual (test-heroui.html)
✅ Three.js para renderização 3D
✅ Cut Views (Session 6)
✅ Voice Comments (Session 6)
✅ Surgery Dashboard (Session 6)
✅ Bone Contact Analysis
✅ Todas as ferramentas de medição
```

O NIfTI e o MPR Viewer se adicionam como um **módulo novo**
sem quebrar nada que existe hoje.

---

## Perguntas em Aberto

```
1. O pipeline de segmentação já gera o volume NIfTI?
   └─ Se não, a conversão é dcm2niix (1 linha de comando)

2. Qual o sistema de coordenadas do OBJ de saída?
   └─ RAS, LPS ou outro? (precisa ser o mesmo do NIfTI)

3. O landmarks.json usa que sistema de coordenadas?
   └─ Para a sincronização MPR↔3D funcionar: deve ser mm no espaço RAS

4. O backend de segmentação é Python?
   └─ Define se o API Backend usa mesma stack (FastAPI) ou separada

5. Integração PACS está planejada?
   └─ Muda o protocolo de ingestão (DICOM network vs upload web)
```

---

**Documento criado em**: 26 de Maio de 2026  
**Baseado em**: Discussão arquitetural Session 6  
**Status**: Proposta Aprovada — Implementação Fase 1 a iniciar
