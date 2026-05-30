/**
 * SchulterPlan Tailwind preset.
 *
 * Usage in a downstream project:
 *
 *   // tailwind.config.js
 *   const schulterplan = require('./UI/css/tailwind.config.cjs');
 *   module.exports = {
 *     presets: [schulterplan],
 *     content: ['./src/**\/*.{html,js,jsx,ts,tsx,vue,svelte}']
 *   };
 *
 * Mirrors tokens.json. Update both if you change a value.
 */
module.exports = {
  theme: {
    extend: {
      colors: {
        bg: {
          base:      '#000000',
          'base-alt': '#0a0a0f',
          surface:   '#18181b',
          card:      'rgba(39,39,42,0.7)',
          'card-hover': 'rgba(63,63,70,0.5)',
          glass:     'rgba(24,24,27,0.6)',
        },
        text: {
          primary:   '#fafafa',
          secondary: '#a1a1aa',
          muted:     '#71717a',
        },
        primary: {
          DEFAULT:  '#17c5b0',
          hover:    '#14b8a6',
          soft:     'rgba(23,197,176,0.12)',
          glow:     'rgba(23,197,176,0.25)',
        },
        accent: {
          DEFAULT:  '#f5a623',
          soft:     'rgba(245,166,35,0.12)',
          glow:     'rgba(245,166,35,0.30)',
        },
        danger:  '#f31260',
        success: '#17c964',
        warning: '#f5a524',
        info:    '#7dd3fc',
        border: {
          DEFAULT: 'rgba(255,255,255,0.08)',
          hover:   'rgba(255,255,255,0.15)',
        },
      },
      borderRadius: {
        sm:   '8px',
        md:   '12px',
        lg:   '16px',
        xl:   '24px',
        pill: '999px',
      },
      boxShadow: {
        sm:     '0 2px 8px rgba(0,0,0,0.30)',
        md:     '0 4px 16px rgba(0,0,0,0.40)',
        lg:     '0 8px 32px rgba(0,0,0,0.50)',
        glow:   '0 0 20px rgba(23,197,176,0.25)',
        accent: '0 0 16px rgba(245,166,35,0.30)',
        focus:  '0 0 0 3px rgba(23,197,176,0.25)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      fontSize: {
        xxs: ['9px',  { lineHeight: '1.2' }],
        xs:  ['10px', { lineHeight: '1.3' }],
        sm:  ['11px', { lineHeight: '1.4' }],
        base:['12px', { lineHeight: '1.4' }],
        md:  ['13px', { lineHeight: '1.4' }],
        lg:  ['14px', { lineHeight: '1.4' }],
        xl:  ['16px', { lineHeight: '1.3' }],
        '2xl':['18px',{ lineHeight: '1.2' }],
        '3xl':['22px',{ lineHeight: '1.1' }],
        '4xl':['32px',{ lineHeight: '1' }],
      },
      letterSpacing: {
        tight:       '-0.3px',
        section:     '1.2px',
        kbd:         '1px',
        tag:         '0.5px',
      },
      backdropBlur: {
        glass: '16px',
      },
      transitionTimingFunction: {
        schulter: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      transitionDuration: {
        fast:   '200ms',
        normal: '300ms',
      },
    },
  },
  plugins: [],
};
