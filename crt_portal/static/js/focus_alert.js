function prepareErrors() {
  // Find elements with class'usa-input--error'
  var errors = document.getElementsByClassName('usa-input--error');
  // add focus to first error
  if (errors.length > 0) {
    // add focus to the first error
    var first_error = errors[0];
    first_error.focus();
    // read first error message
    var error_message = document.getElementsByClassName('usa-alert__body')[0];
    error_message.setAttribute('role', 'alert');
    error_message.setAttribute('aria-live', 'assertive');
  }
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
