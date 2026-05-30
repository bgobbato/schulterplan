/**
 * Tiny DOM helpers used by the example/demo HTMLs.
 * These are NOT a framework — they exist so the templates and
 * kitchen-sink demo are interactive without pulling in React/Vue.
 *
 *   <script src="UI/js/ui-helpers.js"></script>
 */
(function () {

  /** Toggle .active on a button (e.g., btn-accent toggle). */
  window.toggleActive = function (el) {
    if (!el) return;
    const on = el.classList.toggle('active');
    el.setAttribute('aria-pressed', on ? 'true' : 'false');
    return on;
  };

  /** Activate one segment in a .segmented control (siblings deactivate). */
  window.activateSegment = function (segBtn) {
    if (!segBtn) return;
    const parent = segBtn.closest('.segmented');
    if (!parent) return;
    parent.querySelectorAll('.seg-btn').forEach(b => {
      b.classList.remove('active');
      b.setAttribute('aria-selected', 'false');
    });
    segBtn.classList.add('active');
    segBtn.setAttribute('aria-selected', 'true');
  };

  /** Select one implant card (siblings deselect). */
  window.selectImplantCard = function (cardEl) {
    if (!cardEl) return;
    const parent = cardEl.closest('.implant-grid');
    if (!parent) return;
    parent.querySelectorAll('.implant-card').forEach(c => {
      c.classList.remove('selected');
      c.setAttribute('aria-pressed', 'false');
    });
    cardEl.classList.add('selected');
    cardEl.setAttribute('aria-pressed', 'true');
  };

  /** Bump a numeric value inside a .ctrl-label .value element. */
  window.bumpValue = function (valueEl, delta, unit = '') {
    if (!valueEl) return;
    const num = parseFloat(valueEl.textContent) || 0;
    const next = num + delta;
    // Use 1 decimal for degrees, 0 for mm — heuristic.
    const isDeg = (valueEl.textContent || '').includes('°');
    valueEl.textContent = (isDeg ? next.toFixed(1) : next.toString()) + unit;
  };

  /** Auto-wire data-attribute event handlers. Run after DOM ready. */
  function autoWire() {
    document.querySelectorAll('[data-toggle="active"]').forEach(el => {
      el.addEventListener('click', () => toggleActive(el));
    });
    document.querySelectorAll('.segmented .seg-btn').forEach(el => {
      el.addEventListener('click', () => activateSegment(el));
    });
    document.querySelectorAll('.implant-card').forEach(el => {
      el.addEventListener('click', () => selectImplantCard(el));
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoWire);
  } else {
    autoWire();
  }
})();
