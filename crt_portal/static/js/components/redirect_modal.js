import './modal';

(function(root) {
  // note that modal.js must be loaded beforehand
  var modal_el = document.getElementById('external-link--modal');
  var span = document.getElementById('external-link--address');
  var links = document.querySelectorAll('.external-link--popup');
  var continue_button = document.getElementById('external-link--continue');
  var redirect;
  for (var i = 0; i < links.length; i++) {
    var link = links[i];
    link.onclick = function(event) {
      var href = event.target.href;
      event.preventDefault();
      // display the actual redirect link
      span.innerHTML = '<a href="' + href + '">' + href + '</a>';
      root.CRT.openModal(modal_el);
      // set timeout for redirect
      clearTimeout(redirect);
      redirect = setTimeout(function() {
        // only redirect if modal is still visible
        if (modal_el.getAttribute('hidden') === null) {
          window.location.href = href;
        }
      }, 20000);

      continue_button.onclick = function(event) {
        event.preventDefault();
        var href = span.children[0].href;
        window.location.href = href;
      };
    };
  }
  var cancel_modal = document.getElementById('external-link--cancel');
  root.CRT.cancelModal(modal_el, cancel_modal);
})(window);
