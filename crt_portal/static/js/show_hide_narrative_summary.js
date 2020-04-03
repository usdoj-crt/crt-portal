(function () {
  function showSummaryForm() {
    summaryForm.classList.remove('display-none');
    summary.classList.add('display-none');
  }

  function hideSummaryForm() {
    summaryForm.classList.add('display-none');
    summary.classList.remove('display-none');
  }

  function addShowFormHandler() {
    var editButton = summary.getElementsByTagName('button')[0];
    editButton.addEventListener('click', showSummaryForm);
  }

  function setButtonDisabled() {
    if (summaryInput.value.length > 0 && saveButton.hasAttribute('disabled')) {
      saveButton.removeAttribute('disabled');
    } else if (summaryInput.value.length === 0 && !saveButton.hasAttribute('disabled')) {
      saveButton.setAttribute('disabled', true);
    }
  }

  /* created as an empty element and populated if a summary exists */
  var summary = document.getElementById('current-summary');

  /* in contrast, summaryForm will always exist on the page */
  var summaryForm = document.getElementById('comment-actions-summary');
  var summaryInput = summaryForm.getElementsByTagName('textarea')[0];
  var saveButton = summaryForm.getElementsByTagName('button')[0];

  /* disable the save button on page load because there are no changes to save yet */
  saveButton.setAttribute('disabled', 'true');

  /* check to see if there's text in the summary box before making the save button active */
  summaryInput.addEventListener('input', setButtonDisabled);
  saveButton.addEventListener('click', hideSummaryForm);

  if (summary.childElementCount > 0) {
    addShowFormHandler();
    summaryForm.classList.add('display-none');
  }
})();
