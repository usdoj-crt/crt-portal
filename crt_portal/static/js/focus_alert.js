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
  // activate aria live elements for screen reader
  var alerts = document.getElementsByClassName('update-status');
  for (let i = 0; i < alerts.length; i++) {
    let alert = alerts[i];
    var region = document.getElementById('status-update');
    var alertText = alert.textContent;
    var message = document.createElement('p');
    var node = document.createTextNode(alertText);
    message.appendChild(node);
    message.setAttribute('role', 'alert');
    message.setAttribute('class', 'usa-sr-only');
    message.setAttribute(
      'id',
      Math.random()
        .toString(36)
        .substring(2, 15) +
        Math.random()
          .toString(36)
          .substring(2, 15)
    );
    region.appendChild(message);
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
