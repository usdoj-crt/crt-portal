/******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 395:
/***/ (function() {

(function (root, dom) {
  root.CRT = root.CRT || {};

  function autofillTodaysDate(event) {
    var inputEL = event.target.parentElement.getElementsByTagName('input');
    var today = new Date();
    var day = today.getDate(),
        month = today.getMonth() + 1,
        year = today.getFullYear();

    for (i = 0; i < inputEL.length; i++) {
      if (inputEL[i].getAttribute('name').includes('month')) {
        inputEL[i].value = month;
      } else if (inputEL[i].getAttribute('name').includes('day')) {
        inputEL[i].value = day;
      } else if (inputEL[i].getAttribute('name').includes('year')) {
        inputEL[i].value = year;
      }
    }
  }

  var autofill_btns = document.getElementsByClassName('autofill_today_btn');

  for (i = 0; i < autofill_btns.length; i++) {
    autofill_btns[i].addEventListener('click', autofillTodaysDate);
  }

  return root;
})(window, document);

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

/***/ 727:
/***/ (function() {

(function (root, dom) {
  root.CRT = root.CRT || {};

  function toggleFollowUpQuestions(event) {
    var primary_complaint_id = event.target.id;
    var predicate_target_mapping = {
      'id_0-primary_complaint_0': ['div-id_0-public_or_private_employer_0', 'div-id_0-employer_size_0'],
      'id_0-primary_complaint_2': ['div-id_0-public_or_private_school_0'],
      'id_0-primary_complaint_3': ['div-id_0-inside_correctional_facility_0', 'div-id_0-correctional_facility_type_0'],
      'id_0-primary_complaint_5': ['div-id_0-commercial_or_public_place_0', 'div-id_0-other_commercial_or_public_place']
    }; // show

    if (primary_complaint_id in predicate_target_mapping) {
      var targets = predicate_target_mapping[primary_complaint_id];

      for (i = 0; i < targets.length; i++) {
        var target = document.getElementById(targets[i]);
        target.style.display = 'block';
      }
    } // hide


    Object.keys(predicate_target_mapping).forEach(function (primary_id) {
      if (primary_complaint_id != primary_id) {
        var targets = predicate_target_mapping[primary_id];

        for (i = 0; i < targets.length; i++) {
          var target = document.getElementById(targets[i]);
          target.style.display = 'none';
        }
      }
    });
  } // add listeners


  var primary_issues = document.querySelectorAll('*[id^="id_0-primary_complaint_"]');

  for (i = 0; i < primary_issues.length; i++) {
    primary_issues[i].addEventListener('click', toggleFollowUpQuestions);
  }

  return root;
})(window, document);

/***/ }),

/***/ 900:
/***/ (function() {

(function () {
  // see if we're in a browser that supports smooth scrolling, aka not IE11 and some versions of Edge
  // from https://stackoverflow.com/a/53672870
  function supportsSmoothScroll() {
    var supportsScroll = false;

    try {
      var div = document.createElement('div');
      div.scrollTo({
        top: 0,

        get behavior() {
          supportsScroll = true;
          return 'smooth';
        }

      });
    } catch (err) {
      console.log(err);
    }

    return supportsScroll;
  }

  if (supportsSmoothScroll() == true) {
    var offsetHeight;
    var steps;

    (function () {
      // enable smooth scroll with position:sticky header for browsers that support it
      offsetHeight = document.getElementsByClassName('intake-header--progress-bar')[0].getBoundingClientRect().height;
      steps = document.getElementsByClassName('step');

      function smoothScroll(el) {
        el.preventDefault();
        var scrollToSection = document.getElementById(el.target.attributes.href.nodeValue.slice(1));
        var targetTop = scrollToSection.getBoundingClientRect().top;
        var totalOffset = targetTop - offsetHeight - 40; // 40px == padding on card, so title doesn't abut header

        window.scroll({
          top: window.pageYOffset + totalOffset,
          left: window.pageXOffset,
          behavior: 'smooth'
        });
      }

      for (i = 0; i < steps.length; i++) {
        steps[i].addEventListener('click', function (el) {
          smoothScroll(el);
        });
      }
    })();
  } else {
    // if browser doesn't support scrolling and position: sticky, use position: fixed instead
    var header = document.getElementsByClassName('intake-header')[0];
    var barOffset = header.getBoundingClientRect().height;
    var bar = document.getElementsByClassName('intake-header--progress-bar')[0];
    var cards = document.getElementsByClassName('crt-portal-card');
    window.addEventListener('scroll', function () {
      if (window.pageYOffset >= barOffset) {
        bar.style.position = 'fixed';
      } else {
        bar.style.position = 'relative'; // un-stick it when page is scrolled all the way up
      }
    }); // add the class that keeps the card title from getting hidden under the fixed header

    for (i = 0; i < cards.length; i++) {
      cards[i].className = cards[i].className + ' crt-portal-card--space-for-header';
    }
  }
})(window);

/***/ }),

/***/ 533:
/***/ (function() {

// Polyfill Array.from for IE11: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/from
// Production steps of ECMA-262, Edition 6, 22.1.2.1
if (!Array.from) {
  Array.from = function () {
    var toStr = Object.prototype.toString;

    var isCallable = function isCallable(fn) {
      return typeof fn === 'function' || toStr.call(fn) === '[object Function]';
    };

    var toInteger = function toInteger(value) {
      var number = Number(value);

      if (isNaN(number)) {
        return 0;
      }

      if (number === 0 || !isFinite(number)) {
        return number;
      }

      return (number > 0 ? 1 : -1) * Math.floor(Math.abs(number));
    };

    var maxSafeInteger = Math.pow(2, 53) - 1;

    var toLength = function toLength(value) {
      var len = toInteger(value);
      return Math.min(Math.max(len, 0), maxSafeInteger);
    }; // The length property of the from method is 1.


    return function from(arrayLike
    /*, mapFn, thisArg */
    ) {
      // 1. Let C be the this value.
      var C = this; // 2. Let items be ToObject(arrayLike).

      var items = Object(arrayLike); // 3. ReturnIfAbrupt(items).

      if (arrayLike == null) {
        throw new TypeError('Array.from requires an array-like object - not null or undefined');
      } // 4. If mapfn is undefined, then let mapping be false.


      var mapFn = arguments.length > 1 ? arguments[1] : void undefined;
      var T;

      if (typeof mapFn !== 'undefined') {
        // 5. else
        // 5. a If IsCallable(mapfn) is false, throw a TypeError exception.
        if (!isCallable(mapFn)) {
          throw new TypeError('Array.from: when provided, the second argument must be a function');
        } // 5. b. If thisArg was supplied, let T be thisArg; else let T be undefined.


        if (arguments.length > 2) {
          T = arguments[2];
        }
      } // 10. Let lenValue be Get(items, "length").
      // 11. Let len be ToLength(lenValue).


      var len = toLength(items.length); // 13. If IsConstructor(C) is true, then
      // 13. a. Let A be the result of calling the [[Construct]] internal method
      // of C with an argument list containing the single item len.
      // 14. a. Else, Let A be ArrayCreate(len).

      var A = isCallable(C) ? Object(new C(len)) : new Array(len); // 16. Let k be 0.

      var k = 0; // 17. Repeat, while k < len… (also steps a - h)

      var kValue;

      while (k < len) {
        kValue = items[k];

        if (mapFn) {
          A[k] = typeof T === 'undefined' ? mapFn(kValue, k) : mapFn.call(T, kValue, k);
        } else {
          A[k] = kValue;
        }

        k += 1;
      } // 18. Let putStatus be Put(A, "length", len, true).


      A.length = len; // 20. Return A.

      return A;
    };
  }();
}

(function (root, document) {
  var translations = root.CRT.translations;
  var textAreaElem500 = document.getElementsByClassName('word-count-500');
  var textAreaElem10 = document.getElementsByClassName('word-count-10'); // "Words remaining" message

  var wordLimitMessage = document.getElementById('word_limit_message'); // Word limit alert states (visual and for screen readers)

  var wordLimitAlert = document.getElementById('word_limit_alert');
  var wordLimitScreenReaderText = document.getElementById('word_limit_sr_text'); // Wraps both "words remaining" message and alert state

  var wordCountArea = document.getElementById('word_count_area'); // Show word count area for JS-enabled browsers

  if (wordCountArea) {
    wordCountArea.removeAttribute('hidden');
  }

  function onBelowLimit(wordCount, max, textAreaElem) {
    var wordsRemaining = Number(max - wordCount);
    var description = wordsRemaining === 1 ? translations.wordRemainingText : translations.wordsRemainingText; // Unset alert states

    wordLimitAlert.setAttribute('hidden', ''); // hide

    textAreaElem.classList.remove('bg-gold-outline');
    textAreaElem.setAttribute('aria-invalid', 'false'); // Update word counter

    wordLimitMessage.removeAttribute('hidden');
    wordLimitMessage.innerHTML = wordsRemaining + ' ' + description;
  }

  function onEqualOrExceedLimit(value, max, textAreaElem) {
    // Thank you Stack Overflow users Michal and Steve Bradshaw
    // for the examples of trim-to-word-count! https://stackoverflow.com/a/47136558
    // Find all whitespace characters (newline, tab) and use to trim to
    // the max number of words:
    var trimmed = value.split(/(\s+)/, max * 2 - 1).join('');
    textAreaElem.value = trimmed; // Unset message

    wordLimitMessage.setAttribute('hidden', ''); // hide
    // Set alert state

    textAreaElem.setAttribute('aria-invalid', 'true');
    textAreaElem.classList.add('bg-gold-outline');
    wordLimitAlert.removeAttribute('hidden');
    var messageText = String(max) + translations.wordLimitReachedText;
    wordLimitScreenReaderText.innerText = messageText;
  }

  function isA11yAssertive(el) {
    return el.getAttribute('aria-live') === 'assertive';
  }

  function updateWordCount(e, max, textAreaElem) {
    // Initial validation; throw a helpful error if somehow we
    // aren't getting the data we need from the HTML
    if (!max || typeof max !== 'number') {
      throw 'Missing or invalid argument: max';
    }

    if (!textAreaElem) {
      throw 'Missing argument: textAreaElem';
    } // Ignore `e` and read the value directly from the textarea;
    // we want this function to work even if the user hasn't typed
    // anything (e.g. if textarea has initial content).
    //
    // Trim the start of the string because leading whitespace
    // messes with our word count function.


    var value = textAreaElem.value.replace(/^\s+/, ''); // Match groups of non-whitespace characters, i.e. words.

    var wordMatch = value.match(/\S+/g);
    var wordCount = wordMatch ? wordMatch.length : 0;

    if (wordCount >= max) {
      onEqualOrExceedLimit(value, max, textAreaElem);
    } else {
      onBelowLimit(wordCount, max, textAreaElem);
    }

    if (wordCount >= max * 4 / 5 && !isA11yAssertive(wordLimitMessage)) {
      wordLimitMessage.setAttribute('aria-live', 'assertive');
    } else if (isA11yAssertive(wordLimitMessage)) {
      wordLimitMessage.setAttribute('aria-live', 'polite');
    }
  }

  function listenWordCount(e) {
    if (textAreaElem500.length > 0) {
      updateWordCount(e, max = 500, textAreaElem = document.getElementById(textAreaElem500[0].id));
    }

    if (textAreaElem10.length > 0) {
      updateWordCount(e, max = 10, textAreaElem = document.getElementById(textAreaElem10[0].id));
    }
  } // Add listeners only to word-limited elements


  var wordLimitedElements = Array.from(textAreaElem500).concat(Array.from(textAreaElem10));
  wordLimitedElements.forEach(function (element) {
    element.addEventListener('keyup', listenWordCount);
  }); // Fire `updateWordCount()` on page load because textarea may have
  // some initial content; for example if the user fills in the textarea,
  // presses "Next" and then uses the back button to navigate back.
  // assuming only one per page

  listenWordCount();
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
/* harmony import */ var _components_pro_form_show_hide__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(727);
/* harmony import */ var _components_pro_form_show_hide__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_components_pro_form_show_hide__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_autofill_current_date__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(395);
/* harmony import */ var _components_autofill_current_date__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_components_autofill_current_date__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _components_word_count__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(533);
/* harmony import */ var _components_word_count__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_components_word_count__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _components_progress_bar__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(900);
/* harmony import */ var _components_progress_bar__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_components_progress_bar__WEBPACK_IMPORTED_MODULE_4__);





}();
/******/ })()
;
//# sourceMappingURL=proTemplate-a09a2624ee9078185fc6.js.map