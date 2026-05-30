# Surgery Voice - Assistente de Voz Cirúrgico

## Complete Guide for Replication

---

## 📋 Overview

This is a real-time voice assistant for shoulder arthroplasty surgeries. It uses the browser's Web Speech API to transcribe the surgeon's speech and detect surgical phases via keywords, automatically displaying relevant slides on the dashboard.

**Demo:** https://surgery-voice.vercel.app

---

## 🛠️ How to Replicate

### Option 1: Local Server

```bash
# 1. Create a folder
mkdir -p ~/surgery-voice

# 2. Create index.html with the code below

# 3. Start local server
cd ~/surgery-voice
python3 -m http.server 8080

# 4. Open in browser
# http://localhost:8080
```

### Option 2: Vercel Deploy

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Create folder with index.html
mkdir -p surgery-voice
# (copy index.html content to this folder)

# 3. Deploy
vercel --prod

# Or use token (already configured):
# npx vercel deploy <folder> --yes
```

---

## 📄 Complete index.html Code

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hermes - Assistente Cirúrgico</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      min-height: 100vh;
      color: white;
    }
    .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
    header { text-align: center; padding: 20px 0; border-bottom: 1px solid #333; margin-bottom: 20px; }
    h1 { font-size: 1.8rem; color: #4ecdc4; }
    .status-bar { display: flex; justify-content: center; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
    .status { display: flex; align-items: center; gap: 8px; padding: 8px 16px; background: #2d2d44; border-radius: 20px; font-size: 0.9rem; }
    .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #666; }
    .status-dot.active { background: #4ecdc4; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    @media (max-width: 768px) { .main-content { grid-template-columns: 1fr; } }
    .slide-panel { background: #2d2d44; border-radius: 16px; padding: 20px; min-height: 400px; }
    .slide { display: none; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; }
    .slide.active { display: flex; }
    .slide-image { width: 100%; max-width: 400px; height: 250px; background: #1a1a2e; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; border: 2px solid #4ecdc4; }
    .slide-image svg { width: 80px; height: 80px; opacity: 0.5; }
    .slide-title { font-size: 1.5rem; color: #4ecdc4; margin-bottom: 10px; }
    .slide-description { color: #aaa; max-width: 300px; }
    .transcript-panel { background: #2d2d44; border-radius: 16px; padding: 20px; }
    .transcript-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .transcript-header h2 { font-size: 1.1rem; color: #4ecdc4; }
    .mic-button { background: #ff6b6b; border: none; color: white; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-size: 1rem; display: flex; align-items: center; gap: 8px; transition: all 0.3s; }
    .mic-button:hover { background: #ff5252; transform: scale(1.05); }
    .mic-button.listening { background: #4ecdc4; animation: pulse 1s infinite; }
    .transcript-log { background: #1a1a2e; border-radius: 12px; padding: 15px; height: 280px; overflow-y: auto; font-family: monospace; font-size: 0.9rem; }
    .transcript-entry { margin-bottom: 10px; padding: 8px 12px; background: #2d2d44; border-radius: 8px; border-left: 3px solid #4ecdc4; }
    .transcript-entry .keyword { color: #ff6b6b; font-weight: bold; }
    .transcript-entry .timestamp { color: #666; font-size: 0.8rem; }
    .keyword-list { margin-top: 20px; padding: 15px; background: #1a1a2e; border-radius: 12px; }
    .keyword-list h3 { color: #4ecdc4; margin-bottom: 10px; font-size: 0.9rem; }
    .keyword-tags { display: flex; flex-wrap: wrap; gap: 8px; }
    .keyword-tag { background: #4ecdc4; color: #1a1a2e; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; }
    .current-moment { margin-top: 20px; padding: 15px; background: linear-gradient(135deg, #4ecdc4 0%, #45b7aa 100%); border-radius: 12px; text-align: center; }
    .current-moment-label { font-size: 0.8rem; color: #1a1a2e; opacity: 0.8; }
    .current-moment-title { font-size: 1.3rem; font-weight: bold; color: #1a1a2e; }
    .start-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.9); display: flex; align-items: center; justify-content: center; z-index: 1000; }
    .start-overlay.hidden { display: none; }
    .start-button { background: linear-gradient(135deg, #4ecdc4 0%, #45b7aa 100%); border: none; color: #1a1a2e; padding: 20px 40px; border-radius: 30px; font-size: 1.2rem; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 10px; }
    .start-button:hover { transform: scale(1.05); }
  </style>
</head>
<body>
  <div class="start-overlay" id="startOverlay">
    <button class="start-button" id="startButton">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
      </svg>
      Iniciar Assistente de Voz
    </button>
  </div>

  <div class="container">
    <header>
      <h1>🏥 Hermes - Assistente Cirúrgico</h1>
    </header>

    <div class="status-bar">
      <div class="status">
        <div class="status-dot" id="micStatus"></div>
        <span id="micStatusText">Microfone: Inativo</span>
      </div>
      <div class="status">
        <div class="status-dot active"></div>
        <span>Caso: Maria Santos</span>
      </div>
      <div class="status">
        <div class="status-dot active"></div>
        <span>Procedimento: RSA - Direto</span>
      </div>
    </div>

    <div class="main-content">
      <div class="slide-panel">
        <div class="slide active" data-slide="inicio">
          <div class="slide-image">
            <svg viewBox="0 0 24 24" fill="#4ecdc4">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <div class="slide-title">Pronto para Surgery</div>
          <div class="slide-description">Aguardando instruções do cirurgião...</div>
        </div>

        <div class="slide" data-slide="exposicao">
          <div class="slide-image">
            <svg viewBox="0 0 24 24" fill="#4ecdc4">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
          </div>
          <div class="slide-title">📋 Fase: Exposição</div>
          <div class="slide-description">Lado: DIREITO | Paciente: Maria Santos | Glenoid B2</div>
        </div>

        <div class="slide" data-slide="umero">
          <div class="slide-image">
            <svg viewBox="0 0 24 24" fill="#4ecdc4">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
              <circle cx="12" cy="12" r="5"/>
            </svg>
          </div>
          <div class="slide-title">🦴 Osteotomia do Úmero</div>
          <div class="slide-description">Remover osteófitos anteroinferiores conforme planejamento</div>
        </div>

        <div class="slide" data-slide="glenoid">
          <div class="slide-image">
            <svg viewBox="0 0 24 24" fill="#4ecdc4">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
            </svg>
          </div>
          <div class="slide-title">🔩 Glenoid - Preparo</div>
          <div class="slide-description">Versão: -10° | Inclinação: 10° | Fresagem: 4mm</div>
        </div>

        <div class="slide" data-slide="pino">
          <div class="slide-image">
            <svg viewBox="0 0 24 24" fill="#4ecdc4">
              <path d="M14 6l-1-2H5v17h2v-7h5l1 2h7V6h-6zm4 8h-4l-1-2H7V6h5l1 2h5v6z"/>
            </svg>
          </div>
          <div class="slide-title">📍 Guia da Glenoid</div>
          <div class="slide-description">Pino central: 5mm do rebordo inferior | 2 pinos periféricos</div>
        </div>

        <div class="slide" data-slide="implante">
          <div class="slide-image">
            <svg viewBox="0 0 24 24" fill="#4ecdc4">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6zm7 13H5v-.23c0-.62.28-1.2.76-1.58C7.47 15.82 9.64 15 12 15s4.53.82 6.24 2.19c.48.38.76.97.76 1.58V19z"/>
            </svg>
          </div>
          <div class="slide-title">🔧 Trial / Implante</div>
          <div class="slide-description">Glenosfera: 42mm | Baseplate: 8° Post | Haste: 9x170mm</div>
        </div>

        <div class="slide" data-slide="fechamento">
          <div class="slide-image">
            <svg viewBox="0 0 24 24" fill="#4ecdc4">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
          </div>
          <div class="slide-title">✅ Fechamento</div>
          <div class="slide-description">Procedimento concluído! Checklist pós-op realizado.</div>
        </div>
      </div>

      <div class="transcript-panel">
        <div class="transcript-header">
          <h2>🎤 Transcrição em Tempo Real</h2>
          <button class="mic-button" id="micButton">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
            </svg>
            <span>Iniciar</span>
          </button>
        </div>

        <div class="transcript-log" id="transcriptLog">
          <div class="transcript-entry">
            <span class="timestamp">Sistema iniciado</span>
          </div>
        </div>

        <div class="current-moment" id="currentMoment">
          <div class="current-moment-label">MOMENTO ATUAL</div>
          <div class="current-moment-title">Aguardando...</div>
        </div>

        <div class="keyword-list">
          <h3>🎯 Keywords ativas:</h3>
          <div class="keyword-tags">
            <span class="keyword-tag">úmero</span>
            <span class="keyword-tag">glenoid</span>
            <span class="keyword-tag">pino</span>
            <span class="keyword-tag">implante</span>
            <span class="keyword-tag">fechar</span>
            <span class="keyword-tag">exposição</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    // SLIDES CONFIGURATION
    const SLIDES = {
      'inicio': document.querySelector('.slide[data-slide="inicio"]'),
      'exposicao': document.querySelector('.slide[data-slide="exposicao"]'),
      'umero': document.querySelector('.slide[data-slide="umero"]'),
      'glenoid': document.querySelector('.slide[data-slide="glenoid"]'),
      'pino': document.querySelector('.slide[data-slide="pino"]'),
      'implante': document.querySelector('.slide[data-slide="implante"]'),
      'fechamento': document.querySelector('.slide[data-slide="fechamento"]')
    };

    // KEYWORDS - Edit here to add/remove keywords
    const KEYWORDS = {
      'exposicao': ['exposição', 'exposicao', 'incisão', 'incisao', 'delto', 'abordagem'],
      'umero': ['úmero', 'húmero', 'osteotomia úmero', 'osteotomia úmero', 'cabeça úmero', 'cabeça do úmero', 'resecção úmero', 'resecar úmero', 'prep úmero', 'preparar úmero'],
      'glenoid': ['glenoid', 'glenóide', 'glenoide', 'osteotomia glenoid', 'fresa', 'fresagem glenoid', 'prepare glenoid', 'preparar glenoid'],
      'pino': ['pino', 'guia', 'central', 'periférico', 'periferico', 'fio guia', 'fio-guia'],
      'implante': ['implante', 'trial', 'definitivo', 'prótese', 'proteses', 'experimenta', 'teste'],
      'fechamento': ['fechar', 'fechamento', 'sutura', 'close', 'fechar ferida']
    };

    // STATE
    let recognition = null;
    let isListening = false;
    let currentSlide = 'inicio';

    // DOM ELEMENTS
    const micButton = document.getElementById('micButton');
    const micStatus = document.getElementById('micStatus');
    const micStatusText = document.getElementById('micStatusText');
    const transcriptLog = document.getElementById('transcriptLog');
    const currentMomentTitle = document.querySelector('.current-moment-title');
    const startOverlay = document.getElementById('startOverlay');
    const startButton = document.getElementById('startButton');

    // CHANGE SLIDE FUNCTION
    function showSlide(slideName) {
      if (slideName === currentSlide) return;
      document.querySelectorAll('.slide').forEach(slide => slide.classList.remove('active'));
      if (SLIDES[slideName]) {
        SLIDES[slideName].classList.add('active');
        currentSlide = slideName;
        const titles = {
          'inicio': 'Aguardando...',
          'exposicao': '📋 Fase de Exposição',
          'umero': '🦴 Osteotomia do Úmero',
          'glenoid': '🔩 Preparo da Glenoid',
          'pino': '📍 Posicionamento dos Pinos',
          'implante': '🔧 Trial / Implante',
          'fechamento': '✅ Fechamento'
        };
        currentMomentTitle.textContent = titles[slideName] || slideName;
      }
    }

    // DETECT MOMENT FROM TEXT
    function detectMoment(text) {
      const lowerText = text.toLowerCase();
      for (const [moment, keywords] of Object.entries(KEYWORDS)) {
        for (const keyword of keywords) {
          if (lowerText.includes(keyword)) return moment;
        }
      }
      return null;
    }

    // ADD TRANSCRIPT ENTRY
    function addTranscript(text, detectedKeyword = null) {
      const entry = document.createElement('div');
      entry.className = 'transcript-entry';
      const time = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      let content = `<span class="timestamp">${time}</span> - "${text}"`;
      if (detectedKeyword) content += ` <span class="keyword">[${detectedKeyword.toUpperCase()}]</span>`;
      entry.innerHTML = content;
      transcriptLog.appendChild(entry);
      transcriptLog.scrollTop = transcriptLog.scrollHeight;
    }

    // INITIALIZE WEB SPEECH API
    function initSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        alert('Seu navegador não suporta reconhecimento de voz. Use o Chrome.');
        return false;
      }
      recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'pt-BR';
      
      recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
        }
        if (finalTranscript) {
          const moment = detectMoment(finalTranscript);
          addTranscript(finalTranscript, moment);
          if (moment) showSlide(moment);
        }
      };
      
      recognition.onerror = (event) => {
        console.error('Erro no reconhecimento:', event.error);
        if (event.error !== 'no-speech') stopListening();
      };
      
      recognition.onend = () => { if (isListening) recognition.start(); };
      return true;
    }

    // START LISTENING
    function startListening() {
      if (!recognition) { if (!initSpeechRecognition()) return; }
      recognition.start();
      isListening = true;
      micButton.classList.add('listening');
      micButton.querySelector('span').textContent = 'Ouvindo...';
      micStatus.classList.add('active');
      micStatusText.textContent = 'Microfone: Ativo';
    }

    // STOP LISTENING
    function stopListening() {
      isListening = false;
      if (recognition) recognition.stop();
      micButton.classList.remove('listening');
      micButton.querySelector('span').textContent = 'Iniciar';
      micStatus.classList.remove('active');
      micStatusText.textContent = 'Microfone: Inativo';
    }

    // EVENT LISTENERS
    micButton.addEventListener('click', () => { isListening ? stopListening() : startListening(); });
    startButton.addEventListener('click', () => { startOverlay.classList.add('hidden'); startListening(); });
  </script>
</body>
</html>
```

---

## 🔑 Keywords Reference

| Phase | Keywords (Portuguese) |
|-------|----------------------|
| **exposição** | exposição, exposicao, incisão, incisao, delto, abordagem |
| **umero** | úmero, húmero, osteotomia úmero, osteotomia do úmero, cabeça úmero, resecção úmero, resecar úmero, prep úmero |
| **glenoid** | glenoid, glenóide, glenoide, osteotomia glenoid, fresa, fresagem, fresar |
| **pino** | pino, pinos, guia, central, periférico, periférico, fio guia, fio-guia |
| **implante** | implante, trial, definitivo, prótese, próteses, experimenta, teste |
| **fechamento** | fechar, fechamento, sutura, close |

---

## 🌐 Browser Support

| Browser | Platform | Status |
|---------|----------|--------|
| Chrome | Desktop/Android | ✅ Full Support |
| Safari | iOS/Mac | ✅ Full Support |
| Edge | Desktop | ✅ Full Support |
| Firefox | All | ⚠️ Partial |

---

## 📱 How to Use

1. Open the app in a browser (Chrome recommended)
2. Click "Iniciar Assistente de Voz"
3. Allow microphone access
4. Speak naturally during surgery
5. The system will detect keywords and show appropriate slides

---

## ⚙️ Customization

### To add/modify keywords:
Edit the `KEYWORDS` object in the JavaScript section:

```javascript
const KEYWORDS = {
  'exposicao': ['exposição', 'incisão', 'delto'],
  'umero': ['úmero', 'osteotomia úmero'],
  // ... add more phases here
};
```

### To add new slides:
1. Add HTML for the new slide in the `.slide-panel` div
2. Add the slide entry to the `SLIDES` object
3. Add keywords that trigger this slide in `KEYWORDS`

---

## 📞 Support

- **Developer:** Dr. Bruno Gobbato
- **Assistant:** Hermes AI
- **Version:** 1.0

---

*Document created: 2026-05-13*
*Last updated: 2026-05-13*