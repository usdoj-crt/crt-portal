(function(root) {
  // note that modal.js must be loaded beforehand

  function showOmbModal(modal) {
    const cancelModalButton = modal.querySelector('.external-link--cancel');
    root.CRT.cancelModal(modal, cancelModalButton);
    root.CRT.openModal(modal);
  }

  document.querySelectorAll('.open-omb-modal').forEach(openButton => {
    openButton.addEventListener('click', event => {
      event.preventDefault();
      showOmbModal(document.querySelector('.omb--modal'));
    });
  });
})(window);
