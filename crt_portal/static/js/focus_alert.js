function triggerAlert() {
  var alertEl = document.querySelectorAll('.usa-alert__text');

  if (alertEl.length) {
    Array.prototype.slice.call(alertEl).forEach(function(el) {
      el.setAttribute('role', 'alert');
    });
  }
}

window.addEventListener('DOMContentLoaded', triggerAlert);
