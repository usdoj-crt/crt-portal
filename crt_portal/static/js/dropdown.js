(function(root) {
  function Dropdown(el) {
    var el = el;
    var control = el.querySelector('.title');
    var content = el.querySelector('.content');
    var isVisible = true;

    function _toggle() {
      control.setAttribute('aria-expanded', isVisible);
      
      if (isVisible) {
        content.setAttribute('hidden', true);
      } else {
        content.removeAttribute('hidden');
      }
      isVisible = !isVisible;
    }

    _toggle();

    return {
      get el() {
        return el;
      },
      get control() {
        return control;
      },
      toggle(event) {
        if (event.target !== control) {
          return;
        }

        _toggle();
      }
    };
  }

  var dropdowns = Array.prototype.slice.call(document.querySelectorAll('[data-crt-dropdown]'));

  dropdowns.forEach(function(node) {
    var dropdown = Dropdown(node);
    dropdown.control.addEventListener('click', dropdown.toggle);
  });
})(window);
