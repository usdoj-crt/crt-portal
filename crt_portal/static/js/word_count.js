// Polyfill Array.from for IE11: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/from
// Production steps of ECMA-262, Edition 6, 22.1.2.1
if (!Array.from) {
  Array.from = (function () {
    var toStr = Object.prototype.toString;
    var isCallable = function (fn) {
      return typeof fn === 'function' || toStr.call(fn) === '[object Function]';
    };
    var toInteger = function (value) {
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
    var toLength = function (value) {
      var len = toInteger(value);
      return Math.min(Math.max(len, 0), maxSafeInteger);
    };

    // The length property of the from method is 1.
    return function from(arrayLike /*, mapFn, thisArg */) {
      // 1. Let C be the this value.
      var C = this;

      // 2. Let items be ToObject(arrayLike).
      var items = Object(arrayLike);

      // 3. ReturnIfAbrupt(items).
      if (arrayLike == null) {
        throw new TypeError('Array.from requires an array-like object - not null or undefined');
      }

      // 4. If mapfn is undefined, then let mapping be false.
      var mapFn = arguments.length > 1 ? arguments[1] : void undefined;
      var T;
      if (typeof mapFn !== 'undefined') {
        // 5. else
        // 5. a If IsCallable(mapfn) is false, throw a TypeError exception.
        if (!isCallable(mapFn)) {
          throw new TypeError('Array.from: when provided, the second argument must be a function');
        }

        // 5. b. If thisArg was supplied, let T be thisArg; else let T be undefined.
        if (arguments.length > 2) {
          T = arguments[2];
        }
      }

      // 10. Let lenValue be Get(items, "length").
      // 11. Let len be ToLength(lenValue).
      var len = toLength(items.length);

      // 13. If IsConstructor(C) is true, then
      // 13. a. Let A be the result of calling the [[Construct]] internal method
      // of C with an argument list containing the single item len.
      // 14. a. Else, Let A be ArrayCreate(len).
      var A = isCallable(C) ? Object(new C(len)) : new Array(len);

      // 16. Let k be 0.
      var k = 0;
      // 17. Repeat, while k < len… (also steps a - h)
      var kValue;
      while (k < len) {
        kValue = items[k];
        if (mapFn) {
          A[k] = typeof T === 'undefined' ? mapFn(kValue, k) : mapFn.call(T, kValue, k);
        } else {
          A[k] = kValue;
        }
        k += 1;
      }
      // 18. Let putStatus be Put(A, "length", len, true).
      A.length = len;
      // 20. Return A.
      return A;
    };
  })();
}

(function (root, document) {
  var translations = root.CRT.translations;
  var textAreaElem500 = document.getElementsByClassName('word-count-500');
  var textAreaElem10 = document.getElementsByClassName('word-count-10');

  // "Words remaining" message
  var wordLimitMessage = document.getElementById('word_limit_message');

  // Word limit alert states (visual and for screen readers)
  var wordLimitAlert = document.getElementById('word_limit_alert');
  var wordLimitScreenReaderText = document.getElementById('word_limit_sr_text');

  // Wraps both "words remaining" message and alert state
  var wordCountArea = document.getElementById('word_count_area');

  // Show word count area for JS-enabled browsers
  if (wordCountArea) {
    wordCountArea.removeAttribute('hidden');
  }

  function onBelowLimit(wordCount, max, textAreaElem) {
    var wordsRemaining = Number(max - wordCount);
    var description =
      wordsRemaining === 1 ? translations.wordRemainingText : translations.wordsRemainingText;

    // Unset alert states
    wordLimitAlert.setAttribute('hidden', ''); // hide
    textAreaElem.classList.remove('bg-gold-outline');
    textAreaElem.setAttribute('aria-invalid', 'false');

    // Update word counter
    wordLimitMessage.removeAttribute('hidden');
    wordLimitMessage.innerHTML = wordsRemaining + ' ' + description;
  }

  function onEqualOrExceedLimit(value, max, textAreaElem) {
    // Thank you Stack Overflow users Michal and Steve Bradshaw
    // for the examples of trim-to-word-count! https://stackoverflow.com/a/47136558

    // Find all whitespace characters (newline, tab) and use to trim to
    // the max number of words:
    var trimmed = value.split(/(\s+)/, max * 2 - 1).join('');
    textAreaElem.value = trimmed;

    // Unset message
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
    }

    // Ignore `e` and read the value directly from the textarea;
    // we want this function to work even if the user hasn't typed
    // anything (e.g. if textarea has initial content).
    //
    // Trim the start of the string because leading whitespace
    // messes with our word count function.
    var value = textAreaElem.value.replace(/^\s+/, '');

    // Match groups of non-whitespace characters, i.e. words.
    var wordMatch = value.match(/\S+/g);
    var wordCount = wordMatch ? wordMatch.length : 0;

    if (wordCount >= max) {
      onEqualOrExceedLimit(value, max, textAreaElem);
    } else {
      onBelowLimit(wordCount, max, textAreaElem);
    }

    if (wordCount >= (max * 4) / 5 && !isA11yAssertive(wordLimitMessage)) {
      wordLimitMessage.setAttribute('aria-live', 'assertive');
    } else if (isA11yAssertive(wordLimitMessage)) {
      wordLimitMessage.setAttribute('aria-live', 'polite');
    }
  }

  function listenWordCount(e) {
    if (textAreaElem500.length > 0) {
      updateWordCount(
        e,
        (max = 500),
        (textAreaElem = document.getElementById(textAreaElem500[0].id))
      );
    }

    if (textAreaElem10.length > 0) {
      updateWordCount(
        e,
        (max = 10),
        (textAreaElem = document.getElementById(textAreaElem10[0].id))
      );
    }
  }

  // Add listeners only to word-limited elements
  const wordLimitedElements = Array.from(textAreaElem500).concat(Array.from(textAreaElem10));
  wordLimitedElements.forEach(function (element) {
    element.addEventListener('keyup', listenWordCount);
  });

  // Fire `updateWordCount()` on page load because textarea may have
  // some initial content; for example if the user fills in the textarea,
  // presses "Next" and then uses the back button to navigate back.
  // assuming only one per page
  listenWordCount();
})(window, document);
