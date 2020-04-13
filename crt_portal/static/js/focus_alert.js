function prepareErrors() {

  // Find elements with class'usa-input--error'
  var errors = document.getElementsByClassName('usa-input--error');
  // add focus to first error
  if(errors.length > 0){
    var first_error = errors[0]
    first_error.focus()
  }

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
   * Wrapping this call in a setTimeout of zero schedules its execution
   * at the beginning of the next JS frame's call stack. I'm not exactly sure
   * why, but this allows the screen reader to see the 'error' messages.
   */
  setTimeout(prepareErrors, 0);
}

window.addEventListener('DOMContentLoaded', triggerAlert);
