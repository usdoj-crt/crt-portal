function prepareErrors() {
  var pageErrors = document.getElementById('page-errors');
  if (!pageErrors) {
    return;
  }

  // Page level errors begin hidden, and are revealed once the DOM has loaded
  // This makes screen readers think a new element has been inserted into the page.
  pageErrors.classList.remove('display-none');
}

function triggerAlert() {
  /**
   * Wrapping this call in a set timeout of zero schedules it's execution
   * at the beginning of the next JS frame's call stack. I'm not exactly sure
   * why, but this allows the screen reader to see the 'error' messages.
   */
  setTimeout(prepareErrors, 0);
}

window.addEventListener('DOMContentLoaded', triggerAlert);
