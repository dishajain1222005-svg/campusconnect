/* ═══════════════════════════════════════════════════════════════════
   CampusConnect – main.js
   Loading states, deadline countdowns, auto-dismiss alerts.
   NO external dependencies.
   ═══════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Submit button loading state ──────────────────────────────────────
  // Prevents double-submissions (especially on file uploads).
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      // Find the submit button within this form
      const btn = form.querySelector('.btn-submit');
      if (btn && !btn.disabled) {
        btn.classList.add('loading');
        btn.disabled = true;
        // Re-enable after 15 s as a safety fallback
        setTimeout(function () {
          btn.classList.remove('loading');
          btn.disabled = false;
        }, 15000);
      }
    });
  });

  // ── Auto-dismiss flash alerts after 5 seconds ────────────────────────
  document.querySelectorAll('.alert.alert-success, .alert.alert-info').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  // ── Countdown badges on the student dashboard ─────────────────────────
  document.querySelectorAll('.countdown-badge[data-deadline]').forEach(function (el) {
    const deadline = new Date(el.dataset.deadline);
    function update() {
      const diff = deadline - new Date();
      if (diff <= 0) {
        el.textContent = 'Overdue';
        el.classList.replace('bg-warning', 'bg-danger');
        el.classList.remove('text-dark');
        return;
      }
      const h = Math.floor(diff / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      if (h > 48) {
        el.textContent = deadline.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
        return; // no need to update every second for far deadlines
      }
      el.textContent = h > 0 ? h + 'h ' + m + 'm left' : m + 'm left';
      if (diff < 3600000) { // < 1 hour → red
        el.classList.replace('bg-warning', 'bg-danger');
        el.classList.remove('text-dark');
      }
      setTimeout(update, 60000);
    }
    update();
  });

});
