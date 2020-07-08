(function(root, dom) {
  root.CRT = root.CRT || {};

  var previous_onkeydown = dom.onkeydown;

  root.CRT.openModal = function(modal_el) {
    dom.onkeydown = function(event) {
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
    };
    modal_el.removeAttribute('hidden');
    // get first input in this modal so we can focus on it
    // options.focus();
    console.log('TODO: focus');
    dom.body.classList.add('is-modal');
  };

  root.CRT.closeModal = function(modal_el) {
    dom.onkeydown = previous_onkeydown;
    modal_el.setAttribute('hidden', 'hidden');
    dom.body.classList.remove('is-modal');
  };

  root.CRT.cancelModal = function(modal_el, cancel_el) {
    cancel_el.onclick = function(event) {
      event.preventDefault();
      root.CRT.closeModal(modal_el);
    };
  };
})(window, document);
