(function(root) {
  var modal = document.getElementById('print_report');

  var report = document.getElementById('printout_report');
  var showModal = function(event) {
    event.preventDefault();
    if (modal.getAttribute('hidden') !== null) {
      root.CRT.openModal(modal);
    } else {
      root.CRT.closeModal(modal);
    }
  };
  report.addEventListener('click', showModal);
  report.addEventListener('keydown', showModal);

  var cancel_modal = document.getElementById('print_report_cancel');
  root.CRT.cancelModal(modal, cancel_modal);

  // TODO
  // if no options are clicked, disable print button

})(window);
