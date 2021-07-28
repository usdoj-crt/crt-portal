(function(root) {
  document.getElementById('report-form').addEventListener('submit', disableSubmitButton);
  function disableSubmitButton() {
    const submitNextButton = document.getElementById('submit-next');
    const submitButton = document.getElementById('submit-next');
    if (submitNextButton) submitNextButton.disabled = true;
    if (submitButton) submitButton.disabled = true;
  }
})(window);
