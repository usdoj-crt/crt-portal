(function(root) {
  document.getElementById('report-form').addEventListener('submit', disableSubmitButton);
  function disableSubmitButton() {
    const submitNextButton = document.getElementById('submit-next');
    const submitNextTopButton = document.getElementById('submit-next-top');
    const submitNextBottomButton = document.getElementById('submit-next-bottom');
    const submitButton = document.getElementById('submit');
    if (submitNextButton) submitNextButton.disabled = true;
    if (submitNextTopButton) submitNextTopButton.disabled = true;
    if (submitNextBottomButton) submitNextBottomButton.disabled = true;
    if (submitButton) submitButton.disabled = true;
  }
})(window);
