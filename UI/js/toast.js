/**
 * SchulterPlan toast helper.
 *
 *   <div class="toast" id="toast" role="status" aria-live="polite"></div>
 *   <script src="UI/js/toast.js"></script>
 *
 *   showToast('Case loaded.');
 *   showToast('Saved.', { duration: 1500 });
 *   showToast('Failed to import file.', { variant: 'danger' });
 */
(function () {
  let timer = null;

  function showToast(message, opts = {}) {
    const {
      duration = 2500,
      variant = 'default',   // 'default' | 'primary' | 'accent' | 'danger'
      id = 'toast',
    } = opts;

    let el = document.getElementById(id);
    if (!el) {
      el = document.createElement('div');
      el.className = 'toast';
      el.id = id;
      el.setAttribute('role', 'status');
      el.setAttribute('aria-live', 'polite');
      document.body.appendChild(el);
    }

    el.textContent = message;
    el.dataset.variant = variant;

    // Variant styling — kept inline so the helper is self-contained.
    const styles = {
      default: { border: 'var(--border)',                color: 'var(--text-primary)' },
      primary: { border: 'rgba(23,197,176,0.4)',         color: 'var(--primary)'      },
      accent:  { border: 'rgba(245,166,35,0.4)',         color: 'var(--accent)'       },
      danger:  { border: 'rgba(243,18,96,0.4)',          color: 'var(--danger)'       },
    };
    const s = styles[variant] || styles.default;
    el.style.borderColor = s.border;
    el.style.color       = s.color;

    requestAnimationFrame(() => el.classList.add('show'));

    clearTimeout(timer);
    timer = setTimeout(() => el.classList.remove('show'), duration);
  }

  window.showToast = showToast;
})();
