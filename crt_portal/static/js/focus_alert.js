// Overwrites native 'firstElementChild' prototype.
// Adds Document & DocumentFragment support for IE9 & Safari.
(function(constructor) {
  if (constructor && constructor.prototype && constructor.prototype.firstElementChild == null) {
    Object.defineProperty(constructor.prototype, 'firstElementChild', {
      get: function() {
        var node,
          nodes = this.childNodes,
          i = 0;
        while ((node = nodes[i++])) {
          if (node.nodeType === 1) {
            return node;
          }
        }
        return null;
      }
    });
  }
})(window.Node || window.Element);

function find_focusable(element) {
  if (element.nodeName == 'INPUT' || element.nodeName == 'TEXTAREA') {
    return element;
  } else {
    var element = element.firstElementChild;
    return find_focusable(element);
  }
}

function prepareErrors() {
  // Find elements with class'usa-input--error'
  var errors = document.getElementsByClassName('error-focus');
  // add focus to first error
  if (errors.length > 0) {
    // add focus to the first error
    var first_error = errors[0];
    find_focusable(first_error).focus();
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
