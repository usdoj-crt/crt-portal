(function(root, dom) {
  var toggles = dom.querySelectorAll('.td-toggle');
  for (var i = 0; i < toggles.length; i++) {
    var toggle = toggles[i];
    toggle.onclick = function(event) {
      var target = event.target;
      if (target.classList.contains('rotate')) {
        target.classList.remove('rotate');
      } else {
        target.classList.add('rotate');
      }
      event.preventDefault();
    };
  }
})(window, document);
