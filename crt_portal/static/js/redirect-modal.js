(function(root) {
  // note that modal.js must be loaded beforehand
  var modal_el = document.getElementById('external-link--modal');
  var span = document.getElementById('external-link--address');
  var link = document.querySelector('.external-link--popup');
  var redirect;
  link.onclick = function(event) {
    event.preventDefault();
    // display the actual redirect link
    span.href = link.href;
    span.innerText = link.href;
    root.CRT.openModal(modal_el);
    // set timeout for redirect
    clearTimeout(redirect);
    redirect = setTimeout(function() {
      // only redirect if modal is still visible
      if (modal_el.getAttribute('hidden') === null) {
        window.location.href = link.href;
      }
    }, 20000);
  };
  var cancel_modal = document.getElementById('external-link--cancel');
  root.CRT.cancelModal(modal_el, cancel_modal);
  var continue_button = document.getElementById('external-link--continue');
  continue_button.onclick = function(event) {
    event.preventDefault();
    window.location.href = link.href;
  };
})(window);
