/******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 365:
/***/ (function() {

(function (root) {
  var header = document.getElementsByClassName('crt-landing--header')[0];
  var toc = document.getElementById('toc');
  var topNavLink = toc.firstElementChild;
  topNavLink.className = 'usa-sidenav__item usa-current';

  if (toc) {
    var spy = new Gumshoe('#toc a', {});
    toc.addEventListener('gumshoeActivate', function (event) {
      var link = event.detail.link;
      link.className = 'usa-current';
      topNavLink.className = 'usa-sidenav__item';
    });
    toc.addEventListener('gumshoeDeactivate', function (event) {
      var link = event.detail.link;
      link.className = null;
      topNavLink.className = 'usa-sidenav__item usa-current';
    });
  }
})(window);

/***/ }),

/***/ 671:
/***/ (function() {

(function (root, dom) {
  root.CRT = root.CRT || {};
  var previous_onkeydown = dom.onkeydown;
  var focusable_elements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  root.CRT.openModal = function (modal_el) {
    dom.onkeydown = function (event) {
      event = event || window.event;
      var isEscape = false;

      if ('key' in event) {
        isEscape = event.key === 'Escape' || event.key === 'Esc';
      } else {
        isEscape = event.keyCode === 27;
      }

      if (isEscape) {
        root.CRT.closeModal(modal_el);
      }

      var isTab = false;

      if ('key' in event) {
        isTab = event.key === 'Tab';
      } else {
        isTab = event.keyCode === 9;
      }

      if (isTab) {
        var first = modal_el.querySelectorAll(focusable_elements)[0];
        var focusable_content = modal_el.querySelectorAll(focusable_elements);
        var last = focusable_content[focusable_content.length - 1];

        if (event.shiftKey) {
          // browse clickable elements moving backwards
          if (document.activeElement === first) {
            last.focus();
            event.preventDefault();
          }
        } else {
          // browse clickable elements moving forwards
          if (document.activeElement === last) {
            first.focus();
            event.preventDefault();
          }
        }
      }
    };

    modal_el.removeAttribute('hidden'); // get first input in this modal so we can focus on it

    var first = modal_el.querySelectorAll(focusable_elements)[0];
    first.focus();
    dom.body.classList.add('is-modal');
  };

  root.CRT.closeModal = function (modal_el) {
    dom.onkeydown = previous_onkeydown;
    modal_el.setAttribute('hidden', 'hidden');
    dom.body.classList.remove('is-modal');
  };

  root.CRT.cancelModal = function (modal_el, cancel_el, form_el) {
    var dismissModal = function dismissModal(event) {
      if (form_el) {
        form_el.scrollIntoView({
          behavior: 'smooth',
          block: 'end',
          inline: 'nearest'
        });
        form_el.focus();
      }

      event.preventDefault();
      root.CRT.closeModal(modal_el);
    };

    cancel_el.addEventListener('click', dismissModal);
  };
})(window, document);

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be in strict mode.
!function() {
"use strict";

// EXTERNAL MODULE: ./crt_portal/static/js/components/modal.js
var modal = __webpack_require__(671);
;// CONCATENATED MODULE: ./crt_portal/static/js/components/redirect_modal.js


(function (root) {
  // note that modal.js must be loaded beforehand
  var modal_el = document.getElementById('external-link--modal');
  var span = document.getElementById('external-link--address');
  var links = document.querySelectorAll('.external-link--popup');
  var continue_button = document.getElementById('external-link--continue');
  var redirect;

  for (var i = 0; i < links.length; i++) {
    var link = links[i];

    link.onclick = function (event) {
      var href = event.target.href;
      event.preventDefault(); // display the actual redirect link

      span.innerHTML = '<a href="' + href + '">' + href + '</a>';
      root.CRT.openModal(modal_el); // set timeout for redirect

      clearTimeout(redirect);
      redirect = setTimeout(function () {
        // only redirect if modal is still visible
        if (modal_el.getAttribute('hidden') === null) {
          window.location.href = href;
        }
      }, 20000);

      continue_button.onclick = function (event) {
        event.preventDefault();
        var href = span.children[0].href;
        window.location.href = href;
      };
    };
  }

  var cancel_modal = document.getElementById('external-link--cancel');
  root.CRT.cancelModal(modal_el, cancel_modal);
})(window);
// EXTERNAL MODULE: ./crt_portal/static/js/components/highlight_active_header.js
var highlight_active_header = __webpack_require__(365);
;// CONCATENATED MODULE: ./crt_portal/static/js/hceResources.js


}();
/******/ })()
;
//# sourceMappingURL=hceResources.js.map