(function() {
  function Dropdown(el) {
    var el = el;
    var control = el.querySelector('.title');
    var content = el.querySelector('.content');
    var isVisible = true;

    function _toggle() {
      control.setAttribute('aria-expanded', isVisible);

      if (isVisible) {
        content.setAttribute('hidden', true);
        el.classList.remove('expanded');
      } else {
        el.classList.add('expanded');
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
      get isVisible() {
        return isVisible;
      },
      toggle(event) {
        if (event.target !== control) {
          return;
        }

        _toggle();
      },
      hide() {
        isVisible = false;
        content.setAttribute('hidden', true);
        control.setAttribute('aria-expanded', isVisible);
        el.classList.remove('expanded');
      }
    };
  }

  var dropdownNodes = Array.prototype.slice.call(document.querySelectorAll('[data-crt-dropdown]'));

  var dropdowns = dropdownNodes.map(function(node) {
    var dropdown = Dropdown(node);
    return dropdown;
  });

  dropdowns.forEach(function(dropdown) {
    dropdown.control.addEventListener('click', function(event) {
      dropdowns
        .filter(function(dropdown) {
          return dropdown.control !== event.target;
        })
        .forEach(function(d) {
          d.hide();
        });
      dropdown.toggle(event);
    });
  });

  document.body.addEventListener('click', function(event) {
    console.log(event.target)
  });
})(window);
