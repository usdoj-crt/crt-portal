function triggerAlert() {
  // querySelector() will find the first element matching the
  // CSS selector; the JS that follows will announce it.
  var alertEl = document.querySelector('.usa-alert__text');

  if (alertEl) {
    alertEl.setAttribute('role', 'alert');
  }
}

window.onload = triggerAlert();
