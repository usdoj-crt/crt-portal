(function() {
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

  /* created as an empty element and populated if a summary exists */
  var summary = document.getElementById('current-summary');

  /* in contrast, summaryForm will always exist on the page */
  var summaryForm = document.getElementById('comment-actions-summary');
  var saveButton = summaryForm.getElementsByTagName('button')[0];

  saveButton.addEventListener('click', hideSummaryForm);

  if (summary.childElementCount > 0) {
    addShowFormHandler();
    summaryForm.classList.add('display-none');
  }
})();
