# Sistema de Correção de Coordenadas dos Implantes

## O Problema

Os modelos STL dos implantes Implantcast Agilon foram extraídos do
**Effigos Explorer** (plataforma web da Implantcast) e estão em um sistema
de coordenadas diferente da convenção GPS Exactech:

- **Convenção GPS:** o peg (pino central) do implante aponta na direção **-Z**
- **STLs Implantcast:** o peg aponta na direção **+X**
- **STL TechImport:** o peg aponta na direção correta mas está espelhado (180°)

Sem correção, os implantes aparecem deitados ou invertidos na cena 3D.

---

## Diagnóstico

Para entender a orientação de cada STL, foi feita análise de bounding box:

```python
# Script de análise (resumo dos resultados)
# Cada STL foi carregado e o bounding box analisado para determinar
# qual eixo contém a maior extensão (= direção do peg)

glenoid_anat_2_short.stl  →  maior extensão em X  →  peg em +X
glenoid_anat_2_long.stl   →  maior extensão em X  →  peg em +X
glenoid_anat_3_short.stl  →  maior extensão em X  →  peg em +X
glenoid_anat_3_long.stl   →  maior extensão em X  →  peg em +X
glenoid_round_3.stl       →  maior extensão em X  →  peg em +X
techimport.stl            →  peg ok, mas espelhado 180° em torno de X
```

---

## Solução: IMPLANT_CORRECTIONS

Cada modelo tem uma entrada no dicionário `IMPLANT_CORRECTIONS` com:
- **center**: `[cx, cy, cz]` — centro geométrico para centralizar antes de rodar
- **rot**: tipo de rotação a aplicar

```javascript
const IMPLANT_CORRECTIONS = {
  'data/glenoid_anat_2_short.stl': { center: [12.0, 14.1, 11.0], rot: 'ry90' },
  'data/glenoid_anat_2_long.stl':  { center: [14.5,  0.0,  0.0], rot: 'ry90' },
  'data/glenoid_anat_3_short.stl': { center: [13.5,  0.0,  0.0], rot: 'ry90' },
  'data/glenoid_anat_3_long.stl':  { center: [16.0,  0.0,  0.0], rot: 'ry90' },
  'data/glenoid_round_3.stl':      { center: [14.5,  0.0,  0.0], rot: 'ry90' },
  'data/techimport.stl':           { center: [12.5, 12.5,  8.0], rot: 'rx180' },
};
```

---

## Tipos de Rotação

### `ry90` — Rotação de 90° em torno do eixo Y

Usado para todos os modelos **Implantcast Agilon**.

Transforma o peg de +X para -Z (convenção GPS):
```
(x, y, z) → (-z, y, x)
```

Matematicamente: `Ry(90°)` aplicado a cada vértice após centralização.

### `rx180` — Rotação de 180° em torno do eixo X

Usado para o modelo **TechImport**.

Espelha o modelo em Y e Z (corrige o mirror de 180°):
```
(x, y, z) → (x, -y, -z)
```

### `center-only` — Apenas centralização (sem rotação)

Disponível mas não usado atualmente. Centraliza a geometria sem rotação adicional.

---

## Algoritmo: applyImplantCorrection()

```javascript
function applyImplantCorrection(geom, url) {
  const corr = IMPLANT_CORRECTIONS[url];
  if (!corr) return;  // Sem correção para este modelo

  // 1. Centralizar geometria
  const [cx, cy, cz] = corr.center;
  geom.translate(-cx, -cy, -cz);

  // 2. Aplicar rotação
  const pos = geom.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    let x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);

    if (corr.rot === 'ry90') {
      // Ry(90°): (x,y,z) → (-z, y, x)
      pos.setXYZ(i, -z, y, x);
    } else if (corr.rot === 'rx180') {
      // Rx(180°): (x,y,z) → (x, -y, -z)
      pos.setXYZ(i, x, -y, -z);
    }
    // 'center-only': nenhuma rotação adicional
  }

  // 3. Recalcular normais
  pos.needsUpdate = true;
  geom.computeVertexNormals();
}
```

A função é chamada **imediatamente após carregar o STL**, antes de aplicar
as matrizes de transformação do planning.json.

---

## Ordem de Aplicação

```
1. STLLoader carrega geometria bruta
2. applyImplantCorrection():
   a. Centraliza no centro geométrico
   b. Aplica rotação (ry90 ou rx180)
   c. Recalcula normais
3. Matrizes do planning.json posicionam no espaço do paciente:
   implant_to_patient = patientRefToGlenoidRef × transfoFromImplantToLocalGlenoidRef
```

---

## Como Adicionar um Novo Implante

1. Colocar o arquivo STL em `data/`
2. Analisar o bounding box para determinar a orientação do peg
3. Determinar o centro geométrico (bounding box center ou visual)
4. Adicionar entrada em `IMPLANT_CORRECTIONS`:
   ```javascript
   'data/novo_implante.stl': { center: [cx, cy, cz], rot: 'ry90' },
   ```
5. Adicionar entrada em `IMPLANT_TYPES`:
   ```javascript
   'Novo Implante': 'data/novo_implante.stl',
   ```
6. Testar na view "glenoid" — o peg deve apontar para trás (dentro do osso)

---

## Catálogo de Implantes Disponíveis

| Nome na UI | Arquivo | Rotação | Origem |
|------------|---------|---------|--------|
| Agilon Anat. 2 Short | `glenoid_anat_2_short.stl` | ry90 | Implantcast Effigos |
| Agilon Anat. 2 Long | `glenoid_anat_2_long.stl` | ry90 | Implantcast Effigos |
| Agilon Anat. 3 Short | `glenoid_anat_3_short.stl` | ry90 | Implantcast Effigos |
| Agilon Anat. 3 Long | `glenoid_anat_3_long.stl` | ry90 | Implantcast Effigos |
| Agilon Round 3 | `glenoid_round_3.stl` | ry90 | Implantcast Effigos |
| TechImport | `techimport.stl` | rx180 | GPS Exactech |

---

## Referência: Sistemas de Coordenadas

### GPS Exactech (convenção do planning)
- **+X**: Lateral (para fora do corpo)
- **+Y**: Superior
- **+Z**: Anterior (para frente)
- **Peg do implante**: aponta em **-Z** (para posterior/dentro do osso)

### Implantcast Agilon STLs (como foram exportados)
- **+X**: Eixo longo do peg (para fora)
- **+Y**: Superior
- **+Z**: Lateral
- **Peg do implante**: aponta em **+X**

### Após correção Ry(90°)
- O peg passa de +X para -Z ✓
- Compatível com a convenção GPS
