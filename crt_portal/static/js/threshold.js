(function() {
  function showHideThresholdField(e) {
    const wrapper = e.target.closest('.preference-wrapper');
    const thresholdInput = wrapper.querySelector('input[value="threshold"]');
    const thresholdField = wrapper.querySelector('.threshold');
    thresholdField.querySelector('input').value = null;
    thresholdField.hidden = !thresholdInput.checked;
  }

  document.querySelectorAll('.usa-radio__input').forEach(radioInput => {
    radioInput.addEventListener('change', e => {
      showHideThresholdField(e);
    });
  });
})();
