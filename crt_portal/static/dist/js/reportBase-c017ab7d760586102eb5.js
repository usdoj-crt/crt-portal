/******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 882:
/***/ (function() {

(function (root) {
  // note that modal.js must be loaded beforehand
  var modal_el = document.getElementById('contact-info-confirmation--modal');

  function clickSubmit(stepOneSubmitButton) {
    stepOneSubmitButton.addEventListener('click', function (event) {
      var phone_el = document.getElementsByName('0-contact_phone')[0];
      var email_el = document.getElementsByName('0-contact_email')[0];
      var requiredFieldSelected = document.getElementsByName('0-servicemember')[0].checked || document.getElementsByName('0-servicemember')[1].checked;
      var noContactInfo = !phone_el.value && !email_el.value; // If there is contact information OR if the required field is not filled out, no modal is needed

      if (!noContactInfo || !requiredFieldSelected) {
        event.preventDefault();
        submitNextButton.click();
      } else {
        event.preventDefault();
        var cancelModalButton = document.getElementById('external-link--cancel'); // field_el is the field element that will need to be filled out.  We want to focus that field and scroll to it.

        var field_el = {};

        if (noContactInfo || !email_el.value) {
          field_el = email_el;
        } else if (!phone_el.value) {
          field_el = phone_el;
        }

        root.CRT.cancelModal(modal_el, cancelModalButton, field_el);
        root.CRT.openModal(modal_el);
      }
    });
  }

  if (root.CRT.stageNumber === 1) {
    var stepOneSubmitButton = document.getElementById('report-step-1-continue');

    if (stepOneSubmitButton) {
      var submitNextButton = document.getElementById('submit-next');
      var continue_modal_button = document.getElementById('external-link--continue');

      continue_modal_button.onclick = function (event) {
        event.preventDefault();
        submitNextButton.click();
      };

      clickSubmit(stepOneSubmitButton);
    }
  }
})(window);

/***/ }),

/***/ 188:
/***/ (function() {

(function (root) {
  document.getElementById('report-form').addEventListener('submit', disableSubmitButton);

  function disableSubmitButton() {
    var submitNextButton = document.getElementById('submit-next');
    var submitNextTopButton = document.getElementById('submit-next-top');
    var submitButton = document.getElementById('submit');
    if (submitNextButton) submitNextButton.disabled = true;
    if (submitNextTopButton) submitNextTopButton.disabled = true;
    if (submitButton) submitButton.disabled = true;
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

/***/ }),

/***/ 925:
/***/ (function() {

(function (root) {
  root.CRT.isUnsupportedBrowser = function () {
    return Boolean(navigator.userAgent.match(/SamsungBrowser/i));
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
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	!function() {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = function(module) {
/******/ 			var getter = module && module.__esModule ?
/******/ 				function() { return module['default']; } :
/******/ 				function() { return module; };
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	!function() {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = function(exports, definition) {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	!function() {
/******/ 		__webpack_require__.o = function(obj, prop) { return Object.prototype.hasOwnProperty.call(obj, prop); }
/******/ 	}();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be in strict mode.
!function() {
"use strict";
/* harmony import */ var _components_disable_submit_button__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(188);
/* harmony import */ var _components_disable_submit_button__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_components_disable_submit_button__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _components_modal__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(671);
/* harmony import */ var _components_modal__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_components_modal__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_unsupported_browsers__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(925);
/* harmony import */ var _components_unsupported_browsers__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_components_unsupported_browsers__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _components_contact_info_confirmation_modal__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(882);
/* harmony import */ var _components_contact_info_confirmation_modal__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_components_contact_info_confirmation_modal__WEBPACK_IMPORTED_MODULE_3__);




}();
/******/ })()
;
//# sourceMappingURL=reportBase-c017ab7d760586102eb5.js.map