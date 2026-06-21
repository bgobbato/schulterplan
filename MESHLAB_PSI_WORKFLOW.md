# MeshLab Workflow — Preparar escapula para PSI manifold

**Status**: ✅ Validado 31/maio/2026 — produz STL manifold ✓ via manifold-3d.

**Quando usar**: uma vez por caso novo, antes de gerar PSI com manifold-3d.

**Por quê**: marching-cubes produz OBJ não-indexado com vertex drift. manifold-3d
v2.5.1 rejeita esse formato (`Not manifold`). MeshLab re-indexa e valida topologia.

**Input**: `data/scapula.obj` (~238k tris, marching cubes raw)
**Output**: `data/scapula_manifold.obj` (mesmo número de tris, mas indexado e validado)

---

## Passos (~2 minutos)

1. Abre o MeshLab
2. `File → Import Mesh… → data/scapula.obj`
3. Aplica os filtros NESSA ORDEM:

| # | Filter (menu Filters →) | Sub | Defaults? |
|---|---|---|---|
| 1 | Cleaning and Repairing | **Remove Duplicate Vertices** | Sim |
| 2 | Cleaning and Repairing | **Remove Zero Area Faces** | Sim |
| 3 | Cleaning and Repairing | **Repair non Manifold Edges by removing faces** | Sim |
| 4 | Cleaning and Repairing | **Remove Unreferenced Vertices** | Sim |
| 5 | Cleaning and Repairing | **Repair non Manifold Vertices by splitting** | Sim |
| 6 | Remeshing, Simplification, Reconstruction | **Close Holes** | maxHoleSize=30 |
| 7 | Smoothing, Fairing and Deformation | **Laplacian Smooth** | step=1 |

4. (Opcional) Filters → Quality Measure and Computations → **Compute Geometric Measures**
   - Confirma `is_water_tight: True`

5. `File → Export Mesh As…` → **`data/scapula_manifold.obj`** (Ascii ou Binary, ambos OK)

6. Hard refresh `test-psi.html?v=N` no browser

---

## Validação

Console deve mostrar:
```
[PSI Init] Using data/scapula_manifold.obj (cleaned variant)
...
[PSI/Manifold] Scapula merge tol=0.05mm → ~119000 vertices  ← aceita logo na 1ª tolerância
[PSI/Manifold] ✓ Bone subtraction OK
[PSI/Manifold] ✓ K-wire subtraction OK
[PSI/Manifold] ✓ getMesh() OK — Triangles: ~13000
[PSI/Manifold] Verification: { openEdges: 0, nonManifoldEdges: 0 }
```

Se aparecer `[PSI Init] Using data/scapula.obj (raw)`, o fallback ativou — o
`scapula_manifold.obj` não foi salvo no path certo ou o servidor não tem permissão.

---

## Esperado dos filtros

A maioria reporta **"Removed 0 ..."** porque o OBJ raw do marching-cubes JÁ É
topologicamente válido. O que importa é a **re-escrita do arquivo** depois — quando
o MeshLab exporta, ele consolida vertices num OBJ indexado proper, que é o que
manifold-3d precisa.

---

## Automatizar com pymeshlab (futuro)

```python
import pymeshlab

def clean_scapula_for_psi(input_obj: str, output_obj: str):
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(input_obj)
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_null_faces()
    ms.meshing_repair_non_manifold_edges()
    ms.meshing_remove_unreferenced_vertices()
    ms.meshing_repair_non_manifold_vertices()
    ms.meshing_close_holes(maxholesize=30)
    ms.apply_filter('apply_coord_laplacian_smoothing', stepsmoothnum=1)
    ms.save_current_mesh(output_obj)
```

Dispara no pipeline Python logo após o marching-cubes. Output cacheado em S3 com mesma key (`scapula_manifold.obj`).
