# Arquitetura Técnica — GPS Web Planner Implantcast

## Visão Geral

A aplicação é um **single HTML file** (sem build step) que usa Three.js via
ES modules + importmap para renderizar modelos 3D de escápula (OBJ) e implantes
glenoideais (STL) no navegador.

```
┌─────────────────────────────────────────────────────┐
│  Browser (ES Modules)                               │
│  ┌─────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │ HTML/CSS │  │ Three.js │  │ STLLoader/OBJLoader│ │
│  │ (UI)     │  │ (WebGL)  │  │ OrbitControls      │ │
│  └────┬─────┘  └────┬─────┘  └────────┬───────────┘ │
│       │             │                 │              │
│       └─────────────┼─────────────────┘              │
│                     │                                │
│            ┌────────▼────────┐                       │
│            │   App Logic     │                       │
│            │  (state, UI,    │                       │
│            │   transforms)   │                       │
│            └────────┬────────┘                       │
│                     │                                │
│       ┌─────────────┼──────────────┐                 │
│       ▼             ▼              ▼                 │
│  planning.json  scapula.obj   *.stl (implants)       │
└─────────────────────────────────────────────────────┘
```

---

## Fluxo de Dados

### 1. Carregamento inicial

```
1. Browser carrega HTML + CSS
2. importmap resolve Three.js do unpkg CDN
3. Módulo JS inicializa:
   a. Cria Scene, Camera, Renderer, OrbitControls
   b. Carrega planning.json → extrai matrizes de transformação
   c. Carrega scapula.obj → adiciona à cena
   d. Detecta tipo de implante → carrega STL correspondente
   e. Aplica correção de coordenadas (IMPLANT_CORRECTIONS)
   f. Aplica transformação implant→patient via matrizes 4×4
   g. Calcula frame local da glenoide (center, normal, up, right)
   h. Posiciona câmera na view "glenoid" (default)
```

### 2. Import Case (planning.json)

```json
{
  "caseId": "MiriaOE-GPS",
  "side": "LEFT",
  "planning": {
    "glenoidPlate": "LEFT/TechImport/Standard",
    "version": -10.0,
    "inclination": 5.0,
    "transfoFromImplantToLocalGlenoidRef": [4x4 matrix, column-major],
    "patientRefToGlenoidRef": [4x4 matrix, column-major]
  }
}
```

**Cadeia de transformação:**
```
implant_to_patient = patientRefToGlenoidRef × transfoFromImplantToLocalGlenoidRef
```

> **ATENÇÃO:** Apesar do nome, `patientRefToGlenoidRef` transforma de
> Glenoid→Patient (não o contrário). Não inverter esta matriz.

### 3. Frame local da glenoide

Calculado a partir da coluna 3 (translação) da matriz `implant_to_patient`:

```javascript
glenoidCenter = coluna 3 de patientRefToGlenoidRef (posição)
glenoidNormal = coluna 2 de patientRefToGlenoidRef (eixo Z local)
glenoidUp     = coluna 1 de patientRefToGlenoidRef (eixo Y local, negado)
glenoidRight  = coluna 0 de patientRefToGlenoidRef (eixo X local)
```

Este frame é usado para posicionar as 4 câmeras.

---

## Sistema de Câmeras

Todas as views usam o frame local da glenoide como referência:

| View | Posição da câmera | Up vector |
|------|-------------------|-----------|
| **Anterior** | `center + normal × dist` | `(0, 0, 1)` |
| **Glenoid** | `center + normal × dist` | `glenoidUp` |
| **Lateral** | `center + right × dist` | `glenoidUp` |
| **Inferior** | `center - glenoidUp × dist` | `glenoidNormal` |

- `dist = 100` (distância da câmera ao centro)
- Todas as views apontam para `glenoidCenter` via `camera.lookAt()`
- OrbitControls.target = glenoidCenter

---

## Controles de Posição

### Implant Position (rotações angulares)
| Controle | Eixo | Incremento |
|----------|------|------------|
| Retroversão | Rotação em torno do eixo Y local | ±1° |
| Inclinação inferior | Rotação em torno do eixo X local | ±1° |
| Profundidade | Translação no eixo Z local (normal) | ±1mm |

### Translation (translação planar + rotação axial)
| Controle | Eixo | Incremento |
|----------|------|------------|
| ↑↓ (SI) | Translação Y local (superior-inferior) | ±1mm |
| ←→ (AP) | Translação X local (antero-posterior) | ±1mm |
| ↺↻ (Rot) | Rotação axial em torno do eixo Z (normal) | ±1° |

---

## Importmap (Three.js)

```html
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>
<script type="module">
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
  import { STLLoader } from 'three/addons/loaders/STLLoader.js';
  import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
  // ...
</script>
```

> **Importante:** `type="module"` é obrigatório. Não pode coexistir com
> `type="text/babel"` (React CDN). Tentamos usar React + Three.js via CDN
> e não funcionou — abandonamos React em favor de vanilla JS.

---

## Estado da Aplicação (window.GPS)

```javascript
window.GPS = {
  setView: setViewFn,      // Muda a view da câmera
  setImplant: setImplant,  // Muda o modelo de implante
  refreshUI: refreshUI,    // Atualiza valores exibidos na UI
  state: {                 // Estado atual
    version, inclination, depth,
    tx, ty, rotz,
    implantType, showImplant, transparent
  }
};
```

---

## Arquivos-chave e suas responsabilidades

| Arquivo | Linhas | Responsabilidade |
|---------|--------|------------------|
| `test-heroui.html` | ~1670 | UI completa (HTML+CSS+JS) — tema escuro HeroUI |
| `index.html` | ~2230 | UI completa (HTML+CSS+JS) — tema claro, 3 painéis |
| `data/planning.json` | 28 | Dados do caso (matrizes de transformação) |
| `data/scapula.obj` | ~75k | Malha 3D da escápula do paciente |
| `data/*.stl` | variável | Modelos 3D dos implantes Implantcast |
| `server.py` | 534 | Backend Flask (cenários, API) — usado no deploy |

---

## Decisões Técnicas

1. **Single HTML file** — Sem build step, sem node_modules. Tudo inline.
2. **Vanilla JS em vez de React** — React CDN usa `text/babel`, Three.js precisa
   de `type="module"`. Incompatíveis sem bundler.
3. **importmap** — Permite `import * as THREE from 'three'` sem bundler.
4. **Correção por modelo** — Cada STL tem sua própria correção de coordenadas
   (ver `IMPLANT_CORRECTIONS.md`).
5. **Frame local da glenoide** — Extraído das matrizes do planning, não calculado
   geometricamente. Garante consistência com o GPS desktop.
