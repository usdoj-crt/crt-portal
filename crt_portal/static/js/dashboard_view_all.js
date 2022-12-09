(function(root, dom) {
  var toggleAll = dom.querySelector('a.td-toggle-all');
  toggleAll.onclick = function(event) {
    var toggles = dom.querySelectorAll('a.td-toggle');
    var arrow = toggleAll.children[0];
    arrow.classList.contains('rotate')
      ? arrow.classList.remove('rotate')
      : arrow.classList.add('rotate');
    for (var i = 0; i < toggles.length; i++) {
      var image = toggles[i].children[0];
      var id = toggles[i].dataset['id'];
      var summary = dom.getElementById(`tr-additional-${id}`);
      if (image.classList.contains('rotate')) {
        image.classList.remove('rotate');
        summary.setAttribute('hidden', '');
      } else {
        image.classList.add('rotate');
        summary.removeAttribute('hidden');
        // There's no "then" handler since the interaction is a quiet one.
        // Use the network inspector to check on request and response content
        if (toggleAll.dataset['posted'] !== 'true') {
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
      }
    }
    // Set a flag on the toggle so we don't resubmit data multiple times per session.
    toggleAll.dataset['posted'] = 'true';
    event.preventDefault();
  };
})(window, document);
