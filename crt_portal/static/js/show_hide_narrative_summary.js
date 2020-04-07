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

  function setSummaryInputHeight() {
    /* we're not interested in shrinking the box, just in growing it */
    if (parseInt(summaryInput.style.height) < summaryInput.scrollHeight) {
      summaryInput.style.height = (summaryInput.scrollHeight + 16) + 'px';
    }
  }

  /* created as an empty element and populated if a summary exists */
  var summary = document.getElementById('current-summary');

  /* in contrast, summaryForm will always exist on the page */
  var summaryForm = document.getElementById('comment-actions-summary');
  var summaryInput = summaryForm.getElementsByTagName('textarea')[0];
  var saveButton = summaryForm.getElementsByTagName('button')[0];
  var cancelButton = summaryForm.getElementsByClassName('button--cancel')[0];

  /* disable the save button on page load because there are no changes to save yet */
  saveButton.setAttribute('disabled', 'true');

  /* check to see if there's text in the summary box before making the save button active */
  summaryInput.addEventListener('input', setButtonDisabled);

  if (summary.childElementCount > 0) {
    /* set the form's initial height to the height of the existing summary */
    var summaryText = document.getElementById('current-summary-text');
    /* 16 offsets the padding of the input (0.5rem or 8px top and bottom); otherwise short text is cut off */
    summaryInput.style.height = (summaryText.scrollHeight + 16) + 'px';
  } else {
    summaryInput.style.height = '2.5rem';
  }

  /* grow the form to the height of the text */
  summaryInput.addEventListener('input', setSummaryInputHeight);
  saveButton.addEventListener('click', hideSummaryForm);
  cancelButton.addEventListener('click', hideSummaryForm);

  if (summary.childElementCount > 0) {
    addShowFormHandler();
    summaryForm.classList.add('display-none');
  }
})();
