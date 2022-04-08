(function (root) {
  var modal = document.getElementById('routing-guide');
  var toggle = document.getElementById('routing-guide-toggle');

  var showModal = function (event) {
    event.preventDefault();
    if (modal.getAttribute('hidden') !== null) {
      root.CRT.openModal(modal);
    } else {
      root.CRT.closeModal(modal);
    }
  };
  toggle.addEventListener('click', showModal);

  var cancel_modal = document.getElementById('routing_guide_close');
  root.CRT.cancelModal(modal, cancel_modal);
})(window);
