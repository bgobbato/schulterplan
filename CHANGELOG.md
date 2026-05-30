# Changelog — GPS Web Planner Implantcast

## 2026-05-25 — Sessão 5: Humerus Planning Page + Design System Kit

### Feito nesta sessão

#### 1. Pasta `UI/` — Design System Kit exportável
- Criado kit auto-contido para replicar a identidade visual em outros projetos
- 40 arquivos, 292 KB. Estrutura completa:
  - `README.md`, `AGENT_INSTRUCTIONS.md` (regras para outros LLMs), `BRAND.md`, `DESIGN_SYSTEM.md`, `COMPONENTS.md`, `PATTERNS.md`, `ACCESSIBILITY.md`
  - `tokens/` — `tokens.css`, `tokens.json`, `tokens.scss`
  - `css/` — `schulterplan.css` (drop-in single file), `base.css`, `layout.css`, `components.css`, `tailwind.config.cjs`
  - `components/` — 13 snippets HTML de todos os componentes
  - `templates/` — `planner-3col-layout.html`, `dashboard-layout.html`
  - `examples/` — `kitchen-sink.html`, `minimal-app.html`
  - `js/` — `toast.js`, `theme.js`, `ui-helpers.js`
  - `index.html` — portal navegavel + `assets/logo_implantcast.png`

#### 2. Página de Planejamento do Úmero — `humerus.html`
- Página standalone (~1500 linhas) com layout 3 colunas (medidas | dois viewports | ferramentas)
- Viewport esquerdo: SEMPRE anterior (fixo)
- Viewport direito: switchable via segmented (lateral/anterior/superior/inferior)
- Ambos os meshes compartilham UMA `BufferGeometry` — edição propaga automaticamente
- Loader OBJ + auto-conversão para non-indexed + auto-centralização + auto-orientação
- Botões "Humerus" adicionados ao topbar de `test-heroui.html` e `index.html`

#### 3. Auto-orientação robusta
- Detecta `state.longAxis` (eixo mais longo do bbox) e `state.headEnd` (extremidade com mais densidade de vértices = cabeça umeral)
- Funciona com qualquer convenção de eixos do OBJ — sem assumir X/Y/Z up
- Camera positioning em todas as views deriva desses dois valores

#### 4. Ferramenta de Medição 3D
- Mesma da página da escápula (botão "📏 Measure"), cores rotativas, esferas magnéticas, drag detection 5px
- Funciona em ambos os viewports

#### 5. Ferramenta Lasso "Remove Osteophytes"
- Cursor lasso âmbar SVG inline + botão com glow âmbar + label "Lasso Active" quando ativo
- Polígono SVG overlay desenhado em tempo real
- **Highlight vermelho semi-transparente** em ambos os viewports mostra exatamente o que vai ser removido ANTES de soltar
- Pre-projeção de centroides UMA vez no pointerdown (câmera travada) → instantâneo mesmo com 200k+ triângulos
- `requestAnimationFrame` throttle no rebuild do highlight mesh
- Point-in-polygon (ray casting) com bbox cull
- Remoção: splice direto no array de positions (non-indexed)

#### 6. TRÊS controles distintos para gestão de edições
- **Undo** (Cmd/Ctrl+Z, btn dedicado): pop do stack `Float32Array[]` (max 50)
- **Reset** (btn danger, com confirm): clona `state.originalGeometry`, esvazia stack
- **Showing Edited / Showing Original** (topbar): troca ponteiro de geometria, NÃO muta dados, tinge original em azul

#### 7. Medular — corte axial no mid-shaft
- Toggle no sidebar direito
- Aplica `vpL.renderer.clippingPlanes = [plano perpendicular ao longAxis]` (só no viewport direito)
- Câmera reposiciona pra olhar de cima da cabeça em direção ao corte
- Label do viewport muda pra "medullary · axial", segmented control fica desabilitado
- Recenter Cameras também desativa Medular

#### 8. Bug fix — Superior/Inferior invertidos
- Causa: assumia `+longAxis = head end`, mas depende do OBJ
- Solução: usa `state.headEnd` (auto-detectado) para escolher direção
- Como bônus, em todos os side views a cabeça aparece pra cima corretamente

#### 9. UI cleanup
- Removida seção "Mesh" do sidebar esquerdo (contadores de triângulos/vértices)
- Ícone do lasso button redesenhado (loop + corda + nó)
- Atalhos `Esc` (cancela modo) e `Cmd/Ctrl+Z` (undo)

#### 10. Documentação
- `HUMERUS.md` — doc completa da página com tudo sobre arquitetura, state, pipeline de geometria, como trocar modelos, knobs por modelo, limitações
- `CLAUDE.md` atualizado com seção do úmero + como trocar modelo
- Estado atual ainda **não** deployado no Vercel — usuário pediu para validar local primeiro

### Pendências para Próxima Sessão

- [ ] Testar `humerus.html` com outros modelos 3D de úmero (instruções em `HUMERUS.md` §5)
- [ ] Refinar ícones do segmented control (lateral/anterior/superior/inferior) — placeholders
- [ ] Auto-cálculo do ângulo cérvico-diafisário (precisa landmarks manuais)
- [ ] Exportar úmero editado como OBJ para downstream prosthesis fitting
- [ ] Stencil-buffer fill da seção medular pra parecer um contorno 2D sólido
- [ ] File picker para carregar OBJ sem editar código (ver `HUMERUS.md` §5.5 — 10-min add)
- [ ] Adicionar `humerus.html` ao pacote `schulterplan-vercel/` e fazer deploy quando estabilizar
- [ ] **IMPORTANTE persistente**: Criar back surface models para os outros implantes Agilon

---

## 2026-05-24 — Sessão 4: Dashboard Matrix Fix + Vercel Deployment

### Feito nesta sessão

#### 1. Fix: Surgery Dashboard Matrix Transformation
- **Problema**: Dashboard 3D viewports renderizavam com transformação incorreta (implantes flutuantes/deslocados)
- **Causa**: Função `buildI2P()` transponha as matrizes (column-major) em vez de row-major
- **Solução**: Substituir `buildI2P()` por `flatToMatrix4()` com parsing correto de matrices row-major
- **Resultado**: Todos os 6 viewports agora renderizam corretamente
  - Implante posicionado na glenoide
  - Auto-measure mostra valores clínicos (16.1mm inferior, 5.4mm anterior)
  - Center line visível em todas as views

#### 2. Vercel Deployment Package
- Criada pasta completa `schulterplan-vercel/` com:
  - `index.html` (planner 3D)
  - `surgery-dashboard.html` (dashboard TV/monitor)
  - `data/` (todos os modelos 3D + planning.json)
  - `vercel.json`, `package.json`, `.gitignore`
  - Documentação: README.md, DEPLOYMENT.md, VERCEL_SETUP.txt
- Arquivo comprimido: `schulterplan-vercel.tar.gz` (7.0 MB)

#### 3. GitHub + Vercel Deployment
- Repositório GitHub criado: https://github.com/bgobbato/schulterplan
- Deployment bem-sucedido em Vercel
- URL Production: https://schulterplan.vercel.app/
- Build time: 137ms
- Status: ✅ READY

#### 4. Pull Request
- Branch: `fix/dashboard-matrix-transform`
- PR: https://github.com/bgobbato/schulterplan/pull/1
- Descreve todos os fixes e deployment status

### Pendências para Próxima Sessão

- [ ] **IMPORTANTE: Criar back surface models para os outros implantes**
  - Ainda faltam: Agilon Nº3 Short/Long, Round 3, TechImport
  - Necessário para análise de contato nestes modelos
- [ ] Atualizar `index.html` com mesmas features do `test-heroui.html` quando estabilizar
- [ ] Considerar domínio customizado para SchulterPlan (Vercel settings)

---

## 2026-05-24 — Sessão 3: Center Line + Measurement Tool

### Feito nesta sessão

#### 1. Center Line (Linha Central do Implante)
- Linha verde atravessando o centro do implante e toda a escápula
- Direção baseada no eixo do peg (local -Z transformado para world)
- Extensão de 80mm para cada lado do centro do implante
- `depthTest: false` e `renderOrder: 999` para sempre visível
- Toggle via botão "Center Line" (ao lado de Implant On / Transparent)
- Permanece visível mesmo com implante desligado
- Atualiza automaticamente ao mover o implante

#### 2. Ferramenta de Medição 3D
- Botão "📏 Measure" ativa modo de medição
- Clique em 2 pontos no modelo 3D (escápula ou implante) → esferas magnéticas snappam à superfície
- Raycasting contra scapulaMesh + implantMesh para detectar superfícies
- Esferas coloridas (SphereGeometry r=1.2mm, `depthTest: false`)
- Linha conectando os dois pontos com distância em mm
- 6 cores rotativas: cyan, laranja, amarelo, roxo, verde, rosa
- Lista de medições com cor, ID, valor em mm e botão ✕ para deletar
- "Clear All" para limpar todas as medições
- Detecção de drag (5px threshold) para não confundir orbitar com medir
- Seção MEASUREMENTS posicionada entre Bone Contact e Comments

#### 3. Auto Measure — Distância ao Rim da Glenoide
- Botão "Auto Measure" na barra superior (toggle on/off)
- Mede automaticamente a distância do centro do implante ao rim da glenoide:
  - **Inferior** (laranja): centro → rim inferior da glenoide (direção `-glenoidUp`)
  - **Anterior** (cyan): centro → rim anterior da glenoide (direção `glenoidRight` ou `-glenoidRight`, a mais curta)
- Raycasting contra `glenoidRayMesh` (sub-mesh da glenoide, ~11550 triângulos)
- Projeção do centro do implante no plano da face glenoidal + 2mm offset (esferas na superfície)
- Sistema de multi-offset para raycasting: tenta 4.0mm, 2.5mm, 1.5mm — o offset mais alto alcança o rim real sem bater na concavidade, com fallback para offsets menores quando o rim é mais baixo
- Valores esperados: 12–26mm (validado clinicamente)
- Resultados aparecem na lista de medições com labels "Inferior" e "Anterior"
- Clicar novamente no botão limpa as medições automáticas

#### 4. Bug Fix — Double-firing do click handler
- **Problema**: Tanto `addEventListener('click')` quanto `addEventListener('mouseup')` chamavam `onMeasureClick`, causando duplo disparo
- **Causa**: `removeEventListener('click', onMeasureClick)` não funcionava porque o listener era uma arrow function anônima
- **Solução**: Removido o handler `click` duplicado, mantido apenas `mousedown`/`mouseup` com detecção de drag

### Pendências para Próxima Sessão

- [x] **Ferramenta de medição testada e funcionando** ✅
- [x] **Auto Measure implementado e funcionando** ✅
- [ ] **IMPORTANTE: Criar back surface models para os outros implantes**
  - Apenas o **Agilon Nº 2** tem o back surface (`glenoid_anat_2_back.stl`)
  - Faltam: **Agilon Nº 3 Short**, **Agilon Nº 3 Long**, **Agilon Round 3**, **TechImport**
- [ ] Atualizar `index.html` com as mesmas features quando estabilizar

---

## 2026-05-24 — Sessão 2: Bone Contact Analysis (WIP)

### Feito nesta sessão

#### 1. Documentação do Projeto
- Criado `README.md` com visão geral, quick start, estrutura do projeto
- Criado `ARCHITECTURE.md` com fluxo de dados, sistema de câmeras, controles
- Criado `IMPLANT_CORRECTIONS.md` com sistema de correção de coordenadas
- Criado `CHANGELOG.md` (este arquivo)
- Git inicializado com 2 commits (setup + docs)

#### 2. Bone Contact Analysis — Implementação Inicial
- Canvas 2D (160×160) com mapa de calor da área de contato osso-implante
- Porcentagem de contato exibida abaixo do mapa
- Legenda com 4 cores: Embedded (azul), Contact (verde escuro), Near <2mm (verde claro), No contact (cinza)
- Debounce de 400ms para atualização automática ao mover implante
- Hooks em todos os controles de posição, reset, import e seleção de implante

#### 3. Abordagem Técnica do Contact Analysis
- Coleta vértices da escápula em coordenadas world, filtra raio de 35mm do centro glenoidal
- Auto-detecta raio do peg (vértices com z < -3mm no espaço local do implante)
- Exclui zona circular do peg + 1mm de margem da amostragem
- Grid elíptico 28×28 sobre a face do plate, transformado para world coords
- Para cada amostra: busca vértice da escápula mais próximo ao longo do eixo de profundidade
- Tolerância lateral de 2mm (só considera vértices próximos ao raio de profundidade)
- Critério de contato: `depthDist < 2.0mm` (valores negativos = embutido = sempre contato)

### Problemas Encontrados e Correções

| Problema | Causa | Solução | Status |
|----------|-------|---------|--------|
| Peg incluído na análise de contato | Área do peg (cilindro que entra no osso) contava como contato | Auto-detectar raio do peg + excluir zona circular | ✅ Resolvido |
| Distância omnidirecional | Euclidiana em todas as direções; vértices ao lado do plate contavam | Projeção no eixo de profundidade com tolerância lateral 2mm | ✅ Resolvido |
| Implante embutido perdia contato | `Math.abs(depthDist) < threshold` penalizava profundidade | Usar `depthDist < threshold` sem abs (negativo = sempre contato) | ✅ Resolvido |
| Direção de profundidade invertida | Usava `-Z` local do implante transformado, que podia apontar para fora | Usar `glenoidNormal.clone().negate()` diretamente | ✅ Resolvido (código) |
| **Valores de contato ainda imprecisos** | A ser investigado — feedback do usuário indica que a análise não está clinicamente correta | **A investigar na próxima sessão** | ⚠️ Pendente |

### Lições Aprendidas

1. **Direção de profundidade**: Não usar o eixo local do implante transformado pela cadeia
   `I2P = P2G × adjustM × I2G_orig` — o resultado pode inverter o sentido.
   Usar `glenoidNormal` diretamente (extraída da matriz `patientRefToGlenoidRef`).

2. **Contato direcional vs omnidirecional**: A medição de contato deve ser apenas ao longo
   do eixo perpendicular à face do implante (direção DEF+/DEF-), não distância euclidiana.

3. **Embutido = contato**: Na prática clínica, se o implante está mais fundo no osso,
   o contato é total naquela região. O algoritmo não pode penalizar profundidade.

4. **Exclusão do peg**: O peg é a parte cilíndrica que entra no osso e não faz parte
   da superfície de contato. Deve ser excluído automaticamente.

#### 4. Correção da Análise de Contato — Raycasting + Back Surface
- Abordagem por vértices (vertex proximity) abandonada — falsos positivos no rim da glenoide
- Migrado para **raycasting** (Three.js Raycaster) com sub-mesh da glenoide (~11550 triângulos)
- Criado modelo **`glenoid_anat_2_back.stl`** — parte traseira sólida do implante Agilon Nº 2
  - Extraído do Effigos Explorer, serve para Short e Long
  - Usado como superfície de amostragem para o contato (invisível, segue o implante)
  - Correção de coordenadas: center [5.0, 0.0, 0.0], rot ry90
- O mapa de calor agora mostra a **forma anatômica real** do implante (não mais elipse sintética)
- Thresholds finais calibrados com feedback do cirurgião:
  - **Embedded** (azul): depth < -1.0mm
  - **Surface contact** (verde escuro): depth entre -1.0 e 0mm
  - **Near** (verde claro): depth entre 0 e 0.5mm
  - **No contact** (cinza): depth > 0.5mm
  - **depthThreshold**: 0.5mm (critério de contato sim/não)

### Problemas Encontrados e Correções

| Problema | Causa | Solução | Status |
|----------|-------|---------|--------|
| Peg incluído na análise de contato | Área do peg contava como contato | Auto-detectar raio do peg + excluir zona circular | ✅ Resolvido |
| Distância omnidirecional | Euclidiana em todas as direções | Projeção no eixo de profundidade | ✅ Resolvido |
| Implante embutido perdia contato | `Math.abs()` penalizava profundidade | Usar sem abs (negativo = sempre contato) | ✅ Resolvido |
| Direção de profundidade invertida | `-Z` local transformado apontava errado | Usar `glenoidNormal.clone().negate()` | ✅ Resolvido |
| Vertex proximity impreciso | Vértices do rim davam falsos positivos | Migrado para **raycasting** com sub-mesh | ✅ Resolvido |
| Grid elíptico sintético | Não representava a forma real do implante | Usar **back surface model** como amostragem | ✅ Resolvido |
| Thresholds muito altos | 2mm muito permissivo para contato | Calibrado para **0.5mm** com feedback clínico | ✅ Resolvido |

### Pendências para Próxima Sessão

- [ ] **IMPORTANTE: Criar back surface models para os outros implantes**
  - Apenas o **Agilon Nº 2** tem o back surface (`glenoid_anat_2_back.stl`)
  - Faltam: **Agilon Nº 3 Short**, **Agilon Nº 3 Long**, **Agilon Round 3**, **TechImport**
  - Cada implante precisa de um modelo sólido da parte traseira extraído do Effigos Explorer
  - O modelo deve ser colocado em `data/` e adicionado a `BACK_SURFACE_MAP` e `IMPLANT_CORRECTIONS`
  - Sem o back surface, a análise de contato não funciona para esses implantes
- [ ] Atualizar `index.html` com a mesma feature quando estabilizar

---

## 2026-05-23 — Sessão 1: Setup Inicial + Viewer 3D Funcional

### Feito nesta sessão

#### 1. UI HeroUI Dark Theme (`test-heroui.html`)
- Criado layout responsivo com tema escuro inspirado no HeroUI/NextUI
- Fonte Inter, glassmorphism, cards com backdrop-filter
- Palette: teal Implantcast (#17c5b0) como primary, gold (#f5a623) como accent
- Segmented control para views, botões com hover glow

#### 2. Viewer 3D Funcional (Three.js)
- Migração de protótipo React/Babel para vanilla JS + ES modules
- Three.js r160 via importmap (sem bundler, sem node_modules)
- STLLoader para implantes, OBJLoader para escápula
- OrbitControls com damping e limites de zoom
- Iluminação: AmbientLight + 2x DirectionalLight

#### 3. Import Case
- Leitura automática de `data/planning.json` ao abrir a página
- Parsing de matrizes 4×4 (column-major) do formato GPS
- Cálculo do frame local da glenoide (center, normal, up, right)
- Aplicação da cadeia de transformação: Implant → Glenoid → Patient

#### 4. Correção de Coordenadas dos Implantes
- Análise de bounding box de todos os STL (script Python)
- Descoberta: Implantcast STLs têm peg em +X, GPS espera em -Z
- Sistema `IMPLANT_CORRECTIONS` com rotação por modelo:
  - `ry90` para Implantcast Agilon (5 modelos)
  - `rx180` para TechImport (espelhamento 180°)
- Função `applyImplantCorrection()` aplicada após load do STL

#### 5. Views de Câmera
- **Anterior**: Vista frontal clássica
- **Glenoid**: Face-on (olhando de frente para a glenoide)
- **Lateral**: Vista lateral
- **Inferior**: Vista de baixo para cima (adicionada por request)

#### 6. Controles de Posição
- Retroversão (±1°)
- Inclinação inferior (±1°)
- Profundidade (±1mm)
- Translação SI e AP (±1mm)
- Rotação axial CW/CCW (±1°)

#### 7. Translation Pad — Design Cantos Diagonais
- Layout 3×3 com setas direcionais
- Botão ↺ (anti-horário) no canto inferior esquerdo
- Botão ↻ (horário) no canto inferior direito
- Centro da última linha vazio para separação visual

#### 8. Funcionalidades Extras
- Toggle implante on/off
- Toggle transparência do osso
- Seletor de 6 tipos de implante
- Display de valores: SI, AP, Axial Rot
- Botão Reset Position
- Seção de comentários

### Problemas Resolvidos

| Problema | Causa | Solução |
|----------|-------|---------|
| React + Three.js não funcionam juntos via CDN | `text/babel` vs `type="module"` incompatíveis | Abandonar React, usar vanilla JS |
| Implantes Implantcast deitados/rotados | Peg em +X, GPS espera -Z | Rotação Ry(90°) por modelo |
| TechImport espelhado 180° | Orientação invertida | Rotação Rx(180°) |
| Preview servindo versão cached | Python http.server cache | Restart + cache-busting query param |
| Click handlers não funcionam no preview | `setImplant` não exposto no `window.GPS` | Adicionar ao export |

### Notas para Próximas Sessões

- O `server.py` (Flask + SQLite) é do projeto Exactech original e **não é usado**
  pela versão Implantcast. O HTML funciona com qualquer servidor estático.
- Os baseplates `data/baseplate_*.obj` são do catálogo Exactech e não são usados
  com os implantes Implantcast.
- Os cenários em `scenarios/` são do formato GPS Exactech (case.ini) e não do
  formato `planning.json`.
- O deploy em VPS (`deploy/`) foi configurado para a versão Exactech.
