function triggerAlert() {
  // querySelector() will find the first element matching the
  // CSS selector; the JS that follows will announce it.
  var alertEl = document.querySelectorAll('.usa-alert__text');

  if (alertEl.length) {
    Array.prototype.slice.call(alertEl).forEach(function(el) {
      el.setAttribute('role', 'alert');
    });
  }
}

window.addEventListener('DOMContentLoaded', triggerAlert);
