(function(root, dom) {
  const notesField = dom.querySelector('#id_notes');
  function regexEscape(str) {
    return str.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  }
  function updateBatchReports(e, reportBatchControl) {
    e.preventDefault();
    reportBatchControl.classList.toggle('removed');
    reportBatchControl.closest('tr').classList.toggle('removed');
    const id = reportBatchControl.getAttribute('id');
    const note = id + ': [Reason]\n';
    if (reportBatchControl.classList.contains('removed')) {
      notesField.value += note;
      return;
    }
    const notesFieldVal = notesField.value;
    const input = regexEscape(id);
    const regex = new RegExp(input + '.*\\n');
    const newVal = notesFieldVal.replace(regex, '');
    notesField.value = newVal;
  }
  function listenForClick(reportBatchControl) {
    reportBatchControl.addEventListener('click', e => updateBatchReports(e, reportBatchControl));
  }
  function attachListeners() {
    dom.querySelectorAll('.report-batch-control').forEach(listenForClick);
  }
  root.addEventListener('load', attachListeners);
})(window, document);
