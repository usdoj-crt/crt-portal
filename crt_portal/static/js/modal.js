(function (root, dom) {
  root.CRT = root.CRT || {};

  var previous_onkeydown = dom.onkeydown;
  var focusable_elements =
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  root.CRT.openModal = function (modal_el) {
    dom.onkeydown = function (event) {
      event = event || window.event;
      var isEscape = false;
      if ('key' in event) {
        isEscape = event.key === 'Escape' || event.key === 'Esc';
      } else {
        isEscape = event.keyCode === 27;
      }
      if (isEscape) {
        root.CRT.closeModal(modal_el);
      }
      var isTab = false;
      if ('key' in event) {
        isTab = event.key === 'Tab';
      } else {
        isTab = event.keyCode === 9;
      }
      if (isTab) {
        var first = modal_el.querySelectorAll(focusable_elements)[0];
        var focusable_content = modal_el.querySelectorAll(focusable_elements);
        var last = focusable_content[focusable_content.length - 1];
        if (event.shiftKey) {
          // browse clickable elements moving backwards
          if (document.activeElement === first) {
            last.focus();
            event.preventDefault();
          }
        } else {
          // browse clickable elements moving forwards
          if (document.activeElement === last) {
            first.focus();
            event.preventDefault();
          }
        }
      }
    };
    modal_el.removeAttribute('hidden');
    // get first input in this modal so we can focus on it
    var first = modal_el.querySelectorAll(focusable_elements)[0];
    first.focus();
    dom.body.classList.add('is-modal');
  };

  root.CRT.closeModal = function (modal_el) {
    dom.onkeydown = previous_onkeydown;
    modal_el.setAttribute('hidden', 'hidden');
    dom.body.classList.remove('is-modal');
  };

  root.CRT.cancelModal = function (modal_el, cancel_el, form_el) {
    var dismissModal = function (event) {
      if (form_el) {
        form_el.scrollIntoView({ behavior: 'smooth', block: 'end', inline: 'nearest' });
        form_el.focus();
      }
      event.preventDefault();
      root.CRT.closeModal(modal_el);
    };
    cancel_el.addEventListener('click', dismissModal);
  };
})(window, document);
