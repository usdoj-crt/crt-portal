(function(root) {
  document.getElementById('report-form').addEventListener('submit', disableSubmitButton);
  function disableSubmitButton() {
    document.getElementById('submit-next').disabled = true;
  }
})(window);
