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
/* harmony import */ var _components_highlight_active_header__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(365);
/* harmony import */ var _components_highlight_active_header__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_components_highlight_active_header__WEBPACK_IMPORTED_MODULE_0__);

}();
/******/ })()
;
//# sourceMappingURL=privacy-e003fc798cb50583a341.js.map