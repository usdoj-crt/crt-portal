(function(root, dom) {
  var toggles = dom.querySelectorAll('a.td-toggle');
  for (var i = 0; i < toggles.length; i++) {
    var toggle = toggles[i];
    toggle.onclick = function(event) {
      var target = event.currentTarget;
      var id = target.dataset['id'];
      var image = target.children[0];
      var row = dom.getElementById('tr-additional-' + id);
      if (image.classList.contains('rotate')) {
        image.classList.remove('rotate');
        row.setAttribute('hidden', '');
      } else {
        image.classList.add('rotate');
        row.removeAttribute('hidden');

        // There's no "then" handler since the interaction is a quiet one.
        // Use the network inspector to check on request and response content
        window.fetch('/form/api/report/viewed/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': Cookies.get('csrftoken')
          },
          mode: 'same-origin',
          body: JSON.stringify({ report_id: id })
        });
      }
      event.preventDefault();
    };
  }
})(window, document);
