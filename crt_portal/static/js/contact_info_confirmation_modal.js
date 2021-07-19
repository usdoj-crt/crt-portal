(function(root) {
  // note that modal.js must be loaded beforehand
  var modal_el = document.getElementById('contact-info-confirmation--modal');
  var span = document.getElementById('external-link--address');
  var links = document.querySelectorAll('.external-link--popup');
  var continue_button = document.getElementById('external-link--continue');
  var redirect;
  for (var i = 0; i < links.length; i++) {
    var link = links[i];
    console.log('links', links);
    link.onclick = function(event) {
      console.log('document.getElementsByName(\'0-contact_email\')[0].value', document.getElementsByName('0-contact_email')[0].value)
      console.log('in link.onclick')
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

      // set up "continue" button to immediately redirect
      continue_button.onclick = function(event) {
        event.preventDefault();
        var href = span.children[0].href;
        window.location.href = href;
      };
    };
  }
  var cancel_modal = document.getElementById('external-link--cancel');
  root.CRT.cancelModal(modal_el, cancel_modal);

  if (root.CRT.stageNumber === 1) {
    submitButton = document.getElementById('submit-next')
    submitButton.onclick((event) => {
      console.log(event)
      // root.CRT.openModal(contactInfoConfirm);
    })
    var contactInfoConfirm = document.getElementById('contact-info-confirmation--modal');
  }

})(window);
