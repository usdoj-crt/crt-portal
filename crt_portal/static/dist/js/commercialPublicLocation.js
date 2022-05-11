/******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 903:
/***/ (function() {

(function (root, dom) {
  root.CRT = root.CRT || {};

  function doToggle(predicate, target) {
    if (predicate) {
      target.removeAttribute('hidden');
    } else {
      target.setAttribute('hidden', '');
    }
  }

  root.CRT.otherTextInputToggle = function toggleTextInput(selector, index) {
    var parentEl = dom.querySelector('[data-toggle]');
    var selector = selector || '.usa-checkbox';

    if (selector instanceof NodeList) {
      var options = selector;
    } else {
      var options = parentEl.querySelectorAll(selector);
    }

    var index = index || options.length - 1; // Wrapper element for the 'other' option form control

    var otherOptionEl = options[index]; // The actual checkbox or radio button the user will interact with

    var otherOptionFormEl = otherOptionEl.querySelector('[class$="__input"]'); // Wrapper element for the short text description revealed when the 'other' option is selected

    var otherOptionTextEl = parentEl.querySelector('.other-class-option');

    function toggleOtherOptionTextInput(event) {
      var target = event.target;

      if (target.nodeName !== 'INPUT') {
        return;
      }

      if (target.type === 'checkbox') {
        doToggle(otherOptionFormEl.checked, otherOptionTextEl);
      } else if (target.type === 'radio') {
        doToggle(target === otherOptionFormEl, otherOptionTextEl);
      }
    }

    parentEl.addEventListener('click', toggleOtherOptionTextInput);

    if (!otherOptionFormEl.checked) {
      otherOptionTextEl.setAttribute('hidden', '');
    }
  };

  return root;
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
/* harmony import */ var _components_other_show_hide__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(903);
/* harmony import */ var _components_other_show_hide__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_components_other_show_hide__WEBPACK_IMPORTED_MODULE_0__);

}();
/******/ })()
;
//# sourceMappingURL=commercialPublicLocation.js.map