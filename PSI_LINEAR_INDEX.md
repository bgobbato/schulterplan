# PSI Linear Index — Mapeamento Issues ↔ Docs

**Linear project:** [PSI](https://linear.app/bgobbato/project/psi-e52854946bb5)
**Team:** Bgobbato (BGO)
**Política:** toda nova ideia/bug/feature do PSI vira (a) item no MD apropriado E (b) issue no Linear.

---

## Done — Milestones já entregues ✅

| Issue | Título | Doc primária |
|---|---|---|
| [BGO-48](https://linear.app/bgobbato/issue/BGO-48) | Manifold-3d CSG pipeline funcionando (core) | `PSI_IMPLEMENTATION.md` §2-4 |
| [BGO-49](https://linear.app/bgobbato/issue/BGO-49) | MeshLab pre-process workflow + fallback loader | `MESHLAB_PSI_WORKFLOW.md` |
| [BGO-50](https://linear.app/bgobbato/issue/BGO-50) | Patient ID embossed no central cylinder | `PSI_IMPLEMENTATION.md` §1 (Patient ID) |
| [BGO-51](https://linear.app/bgobbato/issue/BGO-51) | Documentação completa do PSI (7 arquivos MD) | Todos os PSI_*.md |

## Todo — Validação clínica (alta prioridade) 🔬

| Issue | Título | Doc | Prioridade |
|---|---|---|---|
| [BGO-52](https://linear.app/bgobbato/issue/BGO-52) | Validação clínica: imprimir protótipo + testar fit em phantom | `PSI_IMPLEMENTATION.md` §8 | High |
| [BGO-53](https://linear.app/bgobbato/issue/BGO-53) | Calibrar BONE_OFFSET / clearance pra fit ajustado | `PSI_NOTES.md` §A | Medium |

## Backlog — Features clínicas / templates 🏥

| Issue | Título | Doc | Prioridade |
|---|---|---|---|
| [BGO-54](https://linear.app/bgobbato/issue/BGO-54) | Template "Tripod With Sleeve" (camisa metálica) | `PSI_NOTES.md` §I | Medium |
| [BGO-55](https://linear.app/bgobbato/issue/BGO-55) | Labels A/P embossed no topo de cada perna | `PSI_NOTES.md` §F | Medium |
| [BGO-56](https://linear.app/bgobbato/issue/BGO-56) | Side mark L/R embossed no central cylinder | `PSI_NOTES.md` §G | Low |

## Backlog — UX / Visualization 🎨

| Issue | Título | Doc | Prioridade |
|---|---|---|---|
| [BGO-57](https://linear.app/bgobbato/issue/BGO-57) | Template selector UI (Tripod vs Tripod With Sleeve) | `PSI_NOTES.md` §I + §E | Medium |
| [BGO-58](https://linear.app/bgobbato/issue/BGO-58) | Advanced mode: sliders pros parâmetros geométricos | `PSI_NOTES.md` §E | Low |
| [BGO-59](https://linear.app/bgobbato/issue/BGO-59) | Encurtar K-wire visualization (cosmetic) | `PSI_NOTES.md` §E | Low |
| [BGO-60](https://linear.app/bgobbato/issue/BGO-60) | Patient ID curved text wrapping around cylinder | `PSI_NOTES.md` §H | Low |

## Backlog — Backend / Producao 🛠

| Issue | Título | Doc | Prioridade |
|---|---|---|---|
| [BGO-61](https://linear.app/bgobbato/issue/BGO-61) | Automatizar MeshLab pre-process via pymeshlab | `MESHLAB_PSI_WORKFLOW.md` (final) + `PSI_NOTES.md` §D1 | Medium |
| [BGO-62](https://linear.app/bgobbato/issue/BGO-62) | Backend CSG service (manifold-3d / pymeshlab server-side) | `PSI_NOTES.md` §D2/D3 | Low |
| [BGO-63](https://linear.app/bgobbato/issue/BGO-63) | Pipeline queue + polling (arquitetura CustomedAI) | `PSI_NOTES.md` §D + `PSI_HAR_ANALYSIS_REPORT.md` | Low |

## Backlog — Fallback engines (robustez) 🛡

| Issue | Título | Doc | Prioridade |
|---|---|---|---|
| [BGO-64](https://linear.app/bgobbato/issue/BGO-64) | Algoritmo close-holes JS pro engine BVH | `PSI_NOTES.md` §C | Low |
| [BGO-65](https://linear.app/bgobbato/issue/BGO-65) | Subtract dome local nos pés (fallback sem escapula) | `PSI_NOTES.md` §B | Low |

## Backlog — Roadmap longo prazo 🚀

| Issue | Título | Doc | Prioridade |
|---|---|---|---|
| [BGO-66](https://linear.app/bgobbato/issue/BGO-66) | Humerus PSI templates (Minimal + Union do CustomedAI) | `PSI_HAR_ANALYSIS_REPORT.md` | Low |
| [BGO-67](https://linear.app/bgobbato/issue/BGO-67) | Auto-suggest leg positions via densidade óssea (CT-driven) | `PSI_IMPLEMENTATION.md` §8 (Long shot) | Low |

---

## Bloqueios / Dependências

```
BGO-52 (impressão protótipo)
  └─► BGO-53 (calibrar BONE_OFFSET) — depende do feedback físico
  └─► BGO-55 (A/P labels) — confirma legibilidade
  └─► BGO-54 (Tripod With Sleeve) — depende da calibração mecânica

BGO-57 (Template selector UI)
  ├─► BGO-54 (implementação Tripod With Sleeve)
  └─► BGO-66 (Humerus templates) — usa mesma infra

BGO-62 (Backend CSG service)
  └─► BGO-63 (Pipeline queue + polling)

BGO-61 (pymeshlab automation)
  └─► BGO-62 (parte do backend completo)
```

---

## Política de manutenção

**Sempre que houver:**
- Nova ideia → adicionar em `PSI_NOTES.md` E criar issue Linear em Backlog
- Bug encontrado → adicionar em `PSI_TROUBLESHOOTING.md` E criar issue Linear em Todo
- Feature começada → mover issue Linear pra In Progress, criar branch git com `gitBranchName` do issue
- Feature pronta → mover pra Done, adicionar entrada no changelog do `PSI_IMPLEMENTATION.md` §7d
- Reorganização de prioridades → atualizar Linear, não esquecer de propagar pra este arquivo

**Para a próxima sessão Claude:**
- `MEMORY.md` carrega `project_psi_implementation_complete.md` automaticamente
- Esse memory tem nota: "consultar Linear PSI project pra issues vivas"
- Este arquivo (`PSI_LINEAR_INDEX.md`) é o índice cruzado autoritativo

---

## Total: 20 issues (4 Done + 16 Backlog/Todo)
