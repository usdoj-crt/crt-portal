(function(root, dom) {
  var toggles = dom.querySelectorAll('a.td-toggle');
  for (var i = 0; i < toggles.length; i++) {
    var toggle = toggles[i];
    toggle.onclick = function(event) {
      var target = event.currentTarget;
      var id = target.dataset['id'];
      var image = target.children[0];
      var row = dom.getElementById('tr-additional-' + id);
      if (target.getAttribute('aria-expanded') === 'true') {
        target.setAttribute('aria-expanded', 'false');
        image.classList.remove('rotate');
        row.setAttribute('hidden', '');
      } else {
        target.setAttribute('aria-expanded', 'true');
        image.classList.add('rotate');
        row.removeAttribute('hidden');

        // There's no "then" handler since the interaction is a quiet one.
        // Use the network inspector to check on request and response content
        window
          .fetch(`/api/reports/${id}/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': Cookies.get('csrftoken')
            },
            mode: 'same-origin',
            body: JSON.stringify({ viewed: true })
          })
          .catch(error => {
            console.error(error);
          });
      }
      event.preventDefault();
    };
  }
})(window, document);
