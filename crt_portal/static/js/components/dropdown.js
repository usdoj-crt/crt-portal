export default function() {
  /**
   * Controls the visibility of a dropdown component
   * @param {HTMLElement} el Node that represents the dropdown
   */
  function Dropdown(el) {
    var el = el;
    var control = el.querySelector('[data-crt-dropdown-control]');
    var content = el.querySelector('.content');
    var isVisible = true;

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
      hide: function() {
        isVisible = false;
        content.setAttribute('hidden', '');
        control.setAttribute('aria-expanded', isVisible);
        el.classList.remove('expanded');
      },
      show: function() {
        isVisible = true;
        content.removeAttribute('hidden');
        control.setAttribute('aria-expanded', isVisible);
        el.classList.add('expanded');
      }
    };
  }

  var dropdownNodes = Array.prototype.slice.call(document.querySelectorAll('[data-crt-dropdown]'));
  var dropdowns = dropdownNodes.map(function(node) {
    var dropdown = Dropdown(node);
    dropdown.hide();

    return dropdown;
  });

  function dropdownToggle(dropdown) {
    if (!dropdown) {
      return;
    }

    if (dropdown.isVisible) {
      dropdown.hide();
    } else {
      closeAllDropdowns();
      dropdown.show();
    }
  }

  function closeAllDropdowns() {
    dropdowns.forEach(function(dropdown) {
      dropdown.hide();
    });
  }

  function hasParentNode(node, isTargetParentFn, maxDepth) {
    var max = maxDepth || 10;
    var depth = 1;
    var currNode = node.parentNode;

    function isMaxDepth(node, currDepth) {
      return node.tagName === 'BODY' || currDepth === max;
    }

    while (currNode) {
      if (isMaxDepth(currNode, depth)) {
        currNode = null;
        break;
      }

      if (isTargetParentFn(currNode)) {
        break;
      }

      currNode = currNode.parentNode;
      depth += 1;
    }

    depth = 1;

    return currNode;
  }

  document.body.addEventListener('click', function(event) {
    /**
     * Determine if the click event happened inside of a dropdown.
     * If so, there are one of two paths we need to take.
     *
     * If the element clicked was inside the dropdown container, do nothing.
     *
     * If the element clicked was exactly a dropdown button:
     *  and the element is already open: close it
     *  otherwise, close all dropodowns and open the one being targeted
     *
     * When click events occur outside of a dropdown, close all open
     * dropdowns
     **/
    var node = hasParentNode(event.target, function(n) {
      if (!n.classList) {
        return false;
      }
      for (var i = 0; i < n.classList.length; i++) {
        if (n.classList[i].indexOf('crt-dropdown') === -1) {
          return false;
        } else {
          return true;
        }
      }
    });

    if (!node) {
      closeAllDropdowns();
    } else {
      // A node here indicates that the click event happened within a dropdown
      var maybeDropdown = dropdowns.filter(function(dropdown) {
        return dropdown.control === event.target;
      })[0];

      dropdownToggle(maybeDropdown);
    }
  });
}
