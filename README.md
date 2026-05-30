# GPS Web Planner — Implantcast Edition

Aplicação web para visualização e planejamento 3D de prótese de ombro (glenoide)
usando modelos **Implantcast Agilon**. Permite ao cirurgião importar um caso
planejado no GPS Exactech, visualizar a escápula + implante em 3D no navegador,
e ajustar posição (retroversão, inclinação, profundidade, translação e rotação axial).

> **Nota:** Este é um projeto experimental / protótipo. Não é um produto oficial.
> Use apenas para fins educacionais e de pesquisa.

---

## Início Rápido

```bash
# 1. Servir localmente
cd "gps-web-planner Implantcast"
python3 -m http.server 8790

# 2. Abrir no navegador
open http://localhost:8790/test-heroui.html    # UI escura (HeroUI)
open http://localhost:8790/index.html          # UI clássica (clara)
```

O caso de teste (`data/planning.json`) é carregado automaticamente ao abrir a página.

---

## Versões da UI

| Arquivo | Tema | Status |
|---------|------|--------|
| `test-heroui.html` | HeroUI dark theme (Inter font, glassmorphism) | **Principal — mais recente** |
| `index.html` | Tema claro clássico (3 painéis: sidebar + viewer + controles) | Funcional, layout desktop |

Ambos compartilham a mesma lógica Three.js e sistema de correção de implantes.

---

## Funcionalidades

- **Viewer 3D** — Three.js com OrbitControls, iluminação ambiente + direcional
- **4 Views de câmera** — Anterior, Glenoid (face-on), Lateral, Inferior
- **Import Case** — Lê `data/planning.json` (formato GPS com matrizes 4×4)
- **6 modelos de implante Implantcast** + 1 TechImport
- **Correção automática de coordenadas** — Cada STL tem rotação/translação corrigida
- **Controles de posição** — Retroversão, inclinação inferior, profundidade
- **Translação XY + rotação axial** — Pad direcional com rotação CW/CCW
- **Transparência** — Toggle para ver implante sob o osso
- **Responsivo** — Funciona em desktop e mobile

---

## Estrutura do Projeto

```
gps-web-planner Implantcast/
├── README.md                  ← Este arquivo
├── ARCHITECTURE.md            ← Arquitetura técnica detalhada
├── IMPLANT_CORRECTIONS.md     ← Sistema de coordenadas dos implantes
│
├── test-heroui.html           ← UI principal (HeroUI dark, ~1670 linhas)
├── index.html                 ← UI clássica (light theme, ~2230 linhas)
├── server.py                  ← Backend Flask + SQLite (cenários, API)
│
├── data/                      ← Modelos 3D e dados do caso
│   ├── planning.json              ← Caso de teste (MiriaOE-GPS, LEFT)
│   ├── scapula.obj                ← Escápula do paciente (OBJ)
│   ├── glenoid_anat_2_short.stl   ← Implantcast Agilon Anat. 2 curto
│   ├── glenoid_anat_2_long.stl    ← Implantcast Agilon Anat. 2 longo
│   ├── glenoid_anat_3_short.stl   ← Implantcast Agilon Anat. 3 curto
│   ├── glenoid_anat_3_long.stl    ← Implantcast Agilon Anat. 3 longo
│   ├── glenoid_round_3.stl        ← Implantcast Agilon Round 3
│   ├── techimport.stl             ← TechImport (genérico)
│   ├── baseplate_*.obj            ← Baseplates Exactech (7 tipos)
│   └── logo_implantcast.png       ← Logo
│
├── Implantcast/               ← Engenharia reversa do Effigos Explorer
│   ├── implantes/                 ← STLs originais da Implantcast
│   ├── extracted_3d/              ← Dados extraídos do HAR
│   ├── Gps-to-obj/                ← Skill de conversão .bin → OBJ
│   ├── *.py                       ← Scripts de análise (OEX, XBIN)
│   └── *.png                      ← Screenshots de referência
│
├── scenarios/                 ← Casos GPS de teste (case.ini + patient.private)
├── deploy/                    ← Config de deploy (Nginx, systemd)
├── CT-test/                   ← Dados DICOM de teste
├── storage/                   ← SQLite database (cenários salvos)
│
├── .claude/
│   └── launch.json            ← Config do preview server (porta 8790)
└── .gitignore
```

---

## Dados do Caso de Teste

O arquivo `data/planning.json` contém o caso **MiriaOE-GPS** (lado esquerdo),
planejado pelo Dr. Bruno Gobbato:

| Parâmetro | Valor |
|-----------|-------|
| Retroversão pré-op | 23° |
| Inclinação inferior pré-op | 5° |
| Subluxação pré-op | 78% |
| Versão planejada | -10° |
| Inclinação planejada | 5° |
| Placa glenoidal | LEFT/TechImport/Standard |

As matrizes `transfoFromImplantToLocalGlenoidRef` e `patientRefToGlenoidRef`
definem a cadeia de transformação completa para posicionar o implante.

---

## Tecnologias

- **Three.js r160** — Renderização WebGL (STLLoader, OBJLoader, OrbitControls)
- **ES Modules + importmap** — Carregamento modular via CDN (unpkg)
- **Vanilla JS** — Sem frameworks (sem React, sem build step)
- **CSS custom properties** — Theming via variáveis CSS
- **Python 3 http.server** — Servidor de desenvolvimento (sem dependências)

---

## Documentos Relacionados

| Arquivo | Conteúdo |
|---------|----------|
| `ARCHITECTURE.md` | Arquitetura técnica, fluxo de dados, sistema de coordenadas |
| `IMPLANT_CORRECTIONS.md` | Por que e como cada STL é corrigido |
| `GUIDE.md` | Guia do usuário (versão Exactech original) |
| `PROJECT.md` | Histórico do projeto (versão Exactech original) |
| `deploy/DEPLOY.md` | Como fazer deploy em VPS |
| `Implantcast/Gps-to-obj/SKILL.md` | Skill de conversão .bin → OBJ |
| `Implantcast/extracted_3d/README_EXTRACAO.txt` | Engenharia reversa do Effigos Explorer |

---

## Autor

**Dr. Bruno Gobbato** — Cirurgião de ombro  
Projeto desenvolvido com assistência de Claude (Anthropic)
