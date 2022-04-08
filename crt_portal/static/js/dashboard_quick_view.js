(function (root, dom) {
  var toggles = dom.querySelectorAll('a.td-toggle');
  for (var i = 0; i < toggles.length; i++) {
    var toggle = toggles[i];
    toggle.onclick = function (event) {
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
      }
      event.preventDefault();
    };
  }
})(window, document);
