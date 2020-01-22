(function(root) {
  root.CRT = root.CRT || {};
  root.CRT.otherTextInputToggle = function toggleTextInput(selector, index) {
    var selector = selector || '.usa-checkbox';
    var dom = root.document;
    var options = dom.querySelectorAll(selector);
    var index = index || options.length - 1;

    // Wapper element for the 'other' option checkbox
    var otherOptionEl = options[index];
    // The actual checkbox the user will interact with
    var otherOptionCheckbox = otherOptionEl.querySelector('[class$="__input"]');
    // Wrapper element for the short text description revealed when the 'other' option is selected
    var otherOptionTextEl = dom.querySelector('.other-class-option');

    function toggleOtherOptionTextInput() {
      if (otherOptionCheckbox.checked) {
        otherOptionTextEl.removeAttribute('hidden');
      } else {
        otherOptionTextEl.setAttribute('hidden', '');
      }
    }

    otherOptionCheckbox.addEventListener('click', toggleOtherOptionTextInput);
    otherOptionTextEl.setAttribute('hidden', '');
  };

  return root;
})(window);
