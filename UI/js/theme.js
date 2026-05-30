/**
 * SchulterPlan runtime theme attacher.
 *
 * Some build systems can't (or won't) import CSS files. In that case,
 * call attachSchulterPlanTokens() to inject :root variables at runtime.
 *
 *   import { attachSchulterPlanTokens } from 'UI/js/theme.js';
 *   attachSchulterPlanTokens();
 *
 * For most projects this is unnecessary — just <link> schulterplan.css.
 */
export const TOKENS = {
  // Surfaces
  '--bg-base':         '#000000',
  '--bg-base-alt':     '#0a0a0f',
  '--bg-surface':      '#18181b',
  '--bg-card':         'rgba(39,39,42,0.7)',
  '--bg-card-hover':   'rgba(63,63,70,0.5)',
  '--bg-glass':        'rgba(24,24,27,0.6)',

  // Borders
  '--border':          'rgba(255,255,255,0.08)',
  '--border-hover':    'rgba(255,255,255,0.15)',

  // Text
  '--text-primary':    '#fafafa',
  '--text-secondary':  '#a1a1aa',
  '--text-muted':      '#71717a',

  // Brand
  '--primary':         '#17c5b0',
  '--primary-hover':   '#14b8a6',
  '--primary-glow':    'rgba(23,197,176,0.25)',
  '--primary-soft':    'rgba(23,197,176,0.12)',
  '--accent':          '#f5a623',
  '--accent-soft':     'rgba(245,166,35,0.12)',
  '--accent-glow':     'rgba(245,166,35,0.30)',

  // Semantic
  '--danger':          '#f31260',
  '--success':         '#17c964',
  '--warning':         '#f5a524',
  '--info':            '#7dd3fc',

  // Radii
  '--radius-sm':       '8px',
  '--radius-md':       '12px',
  '--radius-lg':       '16px',
  '--radius-xl':       '24px',
  '--radius-pill':     '999px',

  // Shadows
  '--shadow-sm':       '0 2px 8px rgba(0,0,0,0.30)',
  '--shadow-md':       '0 4px 16px rgba(0,0,0,0.40)',
  '--shadow-lg':       '0 8px 32px rgba(0,0,0,0.50)',
  '--shadow-glow':     '0 0 20px rgba(23,197,176,0.25)',
  '--shadow-accent':   '0 0 16px rgba(245,166,35,0.30)',

  // Effects
  '--blur':            'blur(16px)',
  '--ease':            'cubic-bezier(0.4, 0, 0.2, 1)',
  '--transition':      '0.2s cubic-bezier(0.4, 0, 0.2, 1)',
  '--transition-slow': '0.3s cubic-bezier(0.4, 0, 0.2, 1)',

  // Type
  '--font-sans':
    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
};

export function attachSchulterPlanTokens(target = document.documentElement) {
  for (const [k, v] of Object.entries(TOKENS)) {
    target.style.setProperty(k, v);
  }
}
