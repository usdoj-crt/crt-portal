function triggerAlert() {
  var alertEl = document.querySelector('.usa-alert__text');
  alertEl.setAttribute('role', 'alert');
}

window.onload = triggerAlert();