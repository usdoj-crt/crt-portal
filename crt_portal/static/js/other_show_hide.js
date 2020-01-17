(function(dom) {
  /**
   * The index of the 'other' option on the protected class form.
   * We target it explicitly becuase while it is currently
   * the last element in the list of options, it might not always be
   */
  var OTHER_OPTION_INDEX = 13;

  // Wapper element for the 'other' option checkbox
  var otherOptionEl = dom.querySelectorAll('.usa-checkbox')[OTHER_OPTION_INDEX];
  // The actual checkbox the user will interact with
  var otherOptionCheckbox = otherOptionEl.querySelector('.usa-checkbox__input');
  // Wrapper element for the short text description revealed when the 'other' option is selected
  var otherOptionTextEl = dom.getElementById('other-class-option');

  function toggleOtherOptionTextInput() {
    if (otherOptionCheckbox.checked) {
      otherOptionTextEl.removeAttribute('hidden');
    } else {
      otherOptionTextEl.setAttribute('hidden', '');
    }
  }

  otherOptionCheckbox.addEventListener('click', toggleOtherOptionTextInput);
  otherOptionTextEl.setAttribute('hidden', '');
})(document);
