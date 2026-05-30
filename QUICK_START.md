# 🚀 Quick Start Guide — SchulterPlan

**Comece a usar SchulterPlan em 5 minutos**

---

## 1️⃣ Acesso Rápido

### Online (Vercel - Pronto para Usar)
```
Escápula Planejador:  https://schulterplan.vercel.app/test-heroui.html
Úmero Planejador:     https://schulterplan.vercel.app/humerus.html
Surgery Dashboard:    https://schulterplan.vercel.app/surgery-dashboard.html
```

### Localmente (Para Desenvolvimento)
```bash
cd "/Users/brunogobbato/Dropbox/Claude Workspace/Advita/gps-web-planner Implantcast"
python3 -m http.server 8000
# Acessar http://localhost:8000/test-heroui.html
```

---

## 2️⃣ Interface Básica (Escápula)

### Painel Esquerdo — Controles
```
┌─ PRE-OP MEASUREMENTS
│  └─ Retroversão: 23°
│  └─ Inferior Incl.: 5°
│  └─ Pre-op Sublux.: 78%
│
├─ IMPLANT SELECTION
│  └─ [Agilon N2] [Anat. 3S] [Anat. 3L] [Round 3] [TechImport]
│
└─ SAVED SCENARIOS
   └─ Scenario 1: empty
   └─ Scenario 2: empty
```

### Viewport Central — 3D View
- **Mouse Drag** → Rotacionar
- **Scroll** → Zoom
- **Right-click Drag** → Pan

### Painel Direito — Posicionamento
```
┌─ IMPLANT POSITION
│  └─ Retroversão: [-10.0°] ← → [+]
│  └─ Inferior Incl.: [5.0°]
│  └─ SI (Y): [0mm]
│  └─ AP (X): [0mm]
│  └─ Axial Rot.: [0°]
│
├─ TRANSLATION
│  └─ [↑] Pan up
│  └─ [←][→] Pan lateral
│  └─ [↓] Pan down
│
└─ BONE CONTACT
   └─ [Visualização de contato]
```

---

## 3️⃣ Cut Views — Como Usar

### Ativar Cut View
1. Clique no botão **"Cut"** na topbar
2. Três opções aparecem: **[Ax] [Cor] [Sag]**

### Escolher Corte
```
[Ax]   → Corte Axial (vista de baixo para cima)
[Cor]  → Corte Coronal (vista frontal)
[Sag]  → Corte Sagital (vista lateral)
```

### Ver Melhor
- Clique em **"Transp."** para modo transparente
- A superfície interna fica escura (marrom #6b5e4a)
- A câmera se reposiciona automaticamente

### Desativar
- Clique no mesmo botão de corte novamente
- Ou clique em "Cut" para desativar tudo

---

## 4️⃣ Voice Comments — Como Gravar

### Preparar
1. Localize a seção **"Comments"** no painel direito
2. Veja o botão 🎤 (microfone)

### Escolher Idioma
```
[PT] → Português Brasileiro 🇧🇷
[EN] → English US 🇺🇸
```

### Gravar Comentário
1. Clique no botão **🎤**
2. Fale seu comentário
3. **Aguarde** até 5 segundos (fim automático)
4. Texto aparece na lista de comentários

### Exemplo de Comentário
```
"Glenoide anterior com pequeno osteófito. 
Implante N2 size 2 short. Ótima profundidade de implantação."
```

---

## 5️⃣ Surgery Dashboard — Revisar Planejamento

### Acessar Dashboard
```
https://schulterplan.vercel.app/surgery-dashboard.html
```

### Ver Resumo de Planejamento
- Painel **"AI"** (direita) mostra:
  - **Key Findings** (pontos-chave do planejamento)
  - **Planning Comments** (comentários de voz transcritos)

### Sincronização Automática
- Dashboard carrega automaticamente os comentários do planejador
- Comentários aparecem com:
  - Timestamp ⏰
  - Bandeira do idioma 🇧🇷 / 🇺🇸
  - Texto completo do comentário

---

## 🎨 Guia Visual Rápido

### Topbar (Barra Superior)
```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] SchulterPlan | Case Miriae-GPS - LEFT - Bruno...    │
│                                                             │
│ [ANTERIOR] [GLENOID] [LATERAL] [INFERIOR] |                │
│ [Implant] [Transp.] [C.Line] [Cut] [Measure] [Import]      │
└─────────────────────────────────────────────────────────────┘
```

### Cores de Referência
```
Primária:    Teal #17c5b0 (Implantcast)
Secundária:  Ouro #f5a623
Textos:      Branco #fafafa
Fundo:       Preto #000000
Superfícies: Cinza escuro #18181b
```

---

## ⌨️ Atalhos Teclado

| Atalho | Ação |
|--------|------|
| `Cmd/Ctrl + Z` | Undo (Humerus/Lasso apenas) |
| `Esc` | Cancelar modo ativo |
| `1` | Vista Anterior |
| `2` | Vista Lateral |
| `3` | Vista Superior |
| `4` | Vista Inferior |

---

## 🔧 Troubleshooting Rápido

### Problema: "Página em branco"
**Solução:**
- Recarregar `F5` ou `Cmd+R`
- Verificar console (`F12` → Console)
- Garantir que dados estão em `data/` folder

### Problema: "Microfone não funciona"
**Solução:**
- Usar Chrome, Safari ou Edge (navegadores com SpeechRecognition)
- Permitir acesso ao microfone (popup do navegador)
- Verificar se há microfone conectado

### Problema: "Cut view cortou o implante"
**Solução:**
- Você está usando uma versão antiga
- Atualizar a página (Ctrl+Shift+R hard refresh)
- Versão Session 6+ corta apenas a escápula

### Problema: "Comentários não aparecem no Dashboard"
**Solução:**
- Verificar se gravou comentário (deve aparecer em Comments primeiro)
- Reload do Dashboard (F5)
- Mesma aba/janela (localStorage é per-origin)

---

## 📚 Documentos para Aprender Mais

| Documento | Quando Ler |
|-----------|-----------|
| [PROJECT_INDEX.md](PROJECT_INDEX.md) | Quero entender toda a arquitetura |
| [SESSION_6_FEATURES.md](SESSION_6_FEATURES.md) | Preciso de detalhes técnicos de Cut Views/Voice/Summary |
| [HUMERUS.md](HUMERUS.md) | Estou trabalhando com planejamento de úmero |
| [CLAUDE.md](CLAUDE.md) | Visão geral do projeto |

---

## 💡 Tips & Tricks

### Medições 3D
```
1. Clique em "Measure"
2. Click ponto 1 na escápula/implante
3. Click ponto 2 
4. Distância aparece em mm
5. Máximo 6 medições (cores diferentes)
6. "Clear All" para limpar
```

### Auto Measure
```
Clique em "Measure"
Mede automaticamente:
  • Distância centro → rim inferior (laranja)
  • Distância centro → rim anterior (cyan)
Valores esperados: 12-26 mm
```

### Modo Transparente
```
[Transp.] ON  → Vê osso + implante com transparência
             → Superfícies internas ficam visíveis
             → Ótimo para análise de profundidade

[Transp.] OFF → Opaco (padrão)
```

### Center Line
```
[C.Line] ON  → Linha verde central do implante
             → Permanece mesmo com implante OFF
             → Útil para alinhamento axial

[C.Line] OFF → Sem linha central
```

---

## 🎯 Workflow Típico de Planejamento

```
1. ABRIR CASO
   └─ test-heroui.html carrega caso MiriaOE-GPS (padrão)

2. SELECIONAR IMPLANTE
   └─ [Agilon N2] ou outro modelo desejado

3. POSICIONAR IMPLANTE
   └─ Ajustar retroversão, inclinação, profundidade
   └─ Visualizar bone contact

4. FAZER CUT VIEW
   └─ [Cut] → [Ax/Cor/Sag] para ver profundidade
   └─ [Transp.] para melhor visualização

5. GRAVAR COMENTÁRIOS
   └─ 🎤 para comentários importantes
   └─ "Profundidade 8mm, ótima cobertura"
   └─ "Sem necessidade de osteotomia"

6. REVISAR NO DASHBOARD
   └─ surgery-dashboard.html
   └─ Ver resumo de planejamento
   └─ Imprimir ou exportar (futuro)

7. SALVAR CENÁRIO (Futuro)
   └─ [SAVED SCENARIOS] → Salvar combinação de parâmetros
```

---

## 🌐 Suporte a Navegadores

```
✅ Chrome 90+      Full support (Speech Recognition nativa)
✅ Safari 14+      Full support (Speech Recognition nativa)
✅ Edge 90+        Full support (Speech Recognition nativa)
⚠️  Firefox 88+    Sem Speech Recognition (comentários por texto)
❌ IE11            Não suportado
```

---

## 📞 Precisa de Ajuda?

### Para Usuários (Médicos)
- Verificar este documento (Quick Start)
- Revisar PROJECT_INDEX.md para referência
- Contatar: bgobbato@gmail.com

### Para Desenvolvedores
- Revisar SESSION_6_FEATURES.md para código
- Revisar HUMERUS.md para página do úmero
- Clonar GitHub: https://github.com/bgobbato/schulterplan

---

## ✨ Novidades Session 6

Três features novas adicionadas:

✅ **Cut Views**
- Cortes precisos no plano do implante
- Câmera se reposiciona automaticamente
- Apenas escápula é cortada (implante inteiro)

✅ **Voice-to-Text Comments**
- Grave comentários por voz
- Transcrição automática (PT-BR/EN-US)
- Persiste em localStorage

✅ **Planning Summary**
- Resumo automático no Surgery Dashboard
- Mostra pontos-chave e comentários
- Sincroniza entre páginas

---

**Última atualização**: 26 de Maio de 2026  
**Versão**: 1.0  
**Status**: ✅ Ready for Clinical Use
