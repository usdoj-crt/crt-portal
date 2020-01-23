(function(root, dom) {
  root.CRT = root.CRT || {};

  function doToggle(predicate, target) {
    if (predicate) {
      target.removeAttribute('hidden');
    } else {
      target.setAttribute('hidden', '');
    }
  }

  root.CRT.otherTextInputToggle = function toggleTextInput(selector, index) {
    var parentEl = dom.querySelector('[data-toggle]');
    var selector = selector || '.usa-checkbox';
    var options = parentEl.querySelectorAll(selector);
    var index = index || options.length - 1;

    // Wapper element for the 'other' option form control
    var otherOptionEl = options[index];
    // The actual checkbox or radio button the user will interact with
    var otherOptionFormEl = otherOptionEl.querySelector('[class$="__input"]');
    // Wrapper element for the short text description revealed when the 'other' option is selected
    var otherOptionTextEl = parentEl.querySelector('.other-class-option');

    function toggleOtherOptionTextInput(event) {
      var target = event.target;

      if (target.nodeName !== 'INPUT') {
        return;
      }

      if (target.type === 'checkbox') {
        doToggle(otherOptionFormEl.checked, otherOptionTextEl);
      } else if (target.type === 'radio') {
        doToggle(target === otherOptionFormEl, otherOptionTextEl);
      }
    }

    parentEl.addEventListener('click', toggleOtherOptionTextInput);
    otherOptionTextEl.setAttribute('hidden', '');
  };

  return root;
})(window, document);
