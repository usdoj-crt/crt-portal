var textAreaElem500 = document.getElementsByClassName("word-count-500");
var textAreaElem10 = document.getElementsByClassName("word-count-10");

// "Words remaining" message
var wordLimitMessage = document.getElementById("word_limit_message");

// Word limit alert states (visual and for screen readers)
var wordLimitAlert = document.getElementById("word_limit_alert");
var wordLimitScreenReaderText = document.getElementById("word_limit_sr_text");

// Wraps both "words remaining" message and alert state
var wordCountArea = document.getElementById("word_count_area");

// Show word count area for JS-enabled browsers
if (wordCountArea) { wordCountArea.removeAttribute('hidden'); }

function onBelowLimit (wordCount, max, textAreaElem) {
  var wordsRemaining = String(max - wordCount);
  var description = (wordsRemaining === 1) ? ' word remaining' : ' words remaining';

  // Unset alert states
  wordLimitAlert.setAttribute('hidden', ''); // hide
  textAreaElem.classList.remove('bg-gold-outline');
  textAreaElem.setAttribute('aria-invalid', 'false');

  // Update word counter
  wordLimitMessage.removeAttribute('hidden');
  wordLimitMessage.innerHTML = wordsRemaining + description;
}

function onEqualOrExceedLimit (value, max, textAreaElem) {
  // Thank you Stack Overflow users Michal and Steve Bradshaw
  // for the examples of trim-to-word-count!
  // https://stackoverflow.com/a/47136558
  var trimmed = value.split(/(\s+)/, ((max * 2) - 1)).join('');
  textAreaElem.value = trimmed;

  // Unset message
  wordLimitMessage.setAttribute('hidden', ''); // hide

  // Set alert state
  textAreaElem.setAttribute('aria-invalid', 'true');
  textAreaElem.classList.add('bg-gold-outline');
  wordLimitAlert.removeAttribute('hidden');

  var messageText = String(max) + ' word limit reached';

  if (wordLimitScreenReaderText.innerText === messageText) {
    wordLimitScreenReaderText.innerText = 'Please finish your summary -- ' + messageText;
  } else {
    wordLimitScreenReaderText.innerText = messageText;
  }
}

function updateWordCount (e, max, textAreaElem) {
  // Initial validation; throw a helpful error if somehow we
  // aren't getting the data we need from the HTML
  if (!max || typeof max !== "number") { throw 'Missing or invalid argument: max'; }
  if (!textAreaElem) { throw 'Missing argument: textAreaElem'; }

  // Ignore `e` and read the value directly from the textarea;
  // we want this function to work even if the user hasn't typed
  // anything (e.g. if textarea has initial content).
  var value = textAreaElem.value;
  var wordCount = value ? value.match(/\S+/g).length : 0;

  if (wordCount >= max) {
    onEqualOrExceedLimit(value, max, textAreaElem);
  } else {
    onBelowLimit(wordCount, max, textAreaElem);
  }

  if (wordCount >= (max * 4 / 5)) {
    wordCountArea.setAttribute('aria-live', 'assertive');
  } else {
    wordCountArea.setAttribute('aria-live', 'polite');
  }
};

function listenWordCount (e) {
  if (textAreaElem500.length > 0) {
    updateWordCount(e, max=500, textAreaElem=document.getElementById(textAreaElem500[0].id));
  };

  if (textAreaElem10.length > 0) {
    updateWordCount(e, max=10, textAreaElem=document.getElementById(textAreaElem10[0].id));
  };
};

document.addEventListener('keyup', listenWordCount);

// Fire `updateWordCount()` on page load because textarea may have
// some initial content; for example if the user fills in the textarea,
// presses "Next" and then uses the back button to navigate back.
// assuming only one per page
listenWordCount();