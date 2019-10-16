var textAreaElem = document.getElementById("id_1-violation_summary");

// "Words remaining" message
var wordLimitMessage = document.getElementById("word_limit_message");

// Word limit alert state
var wordLimitAlert = document.getElementById("word_limit_alert");

// Wraps both "words remaining" message and alert state
var wordCountArea = document.getElementById("word_count_area");

// Show word count area for JS-enabled browsers
if (wordCountArea) { wordCountArea.removeAttribute('hidden'); }

function onBelowLimit (wordCount) {
  var wordsRemaining = String(500 - wordCount);
  var description = (wordsRemaining === 1) ? ' word remaining' : ' words remaining';

  // Unset alert states
  wordLimitAlert.setAttribute('hidden', ''); // hide
  textAreaElem.classList.remove('bg-gold-outline');
  textAreaElem.setAttribute('aria-invalid', 'false');

  // Update word counter
  wordLimitMessage.removeAttribute('hidden');
  wordLimitMessage.innerHTML = wordsRemaining + description;
}

function onEqualOrExceedLimit (wordCount) {
  // Trim the text down to the first 500 words:
  var trimmed = textAreaElem.value.split(" ", 500).join(" ")
                                  .split("\t", 500).join("\t")
                                  .split("\n", 500).join("\n");
  textAreaElem.value = trimmed;

  // Unset message
  wordLimitMessage.setAttribute('hidden', ''); // hide

  // Set alert state
  textAreaElem.setAttribute('aria-invalid', 'true');
  textAreaElem.classList.add('bg-gold-outline');
  wordLimitAlert.removeAttribute('hidden');
}

function updateWordCountArea (e) {
    // Ignore `e` and read the value directly from the textarea here;
    // we want this function to work even if the user hasn't typed
    // anything (e.g. if textarea has initial content).
    var value = textAreaElem.value;
    var wordCount = value ? value.match(/\S+/g).length : 0;

    if (wordCount >= 500) {
      onEqualOrExceedLimit(wordCount);
    } else {
      onBelowLimit(wordCount);
    }

    if (wordCount >= 400) {
      wordCountArea.setAttribute('aria-live', 'assertive');
    } else {
      wordCountArea.setAttribute('aria-live', 'polite');
    }
};

if (textAreaElem) {
  // Fire `updateWordCount()` on page load because textarea may have
  // some initial content; for example if the user fills in the textarea,
  // presses "Next" and then uses the back button to navigate back.
  updateWordCountArea();

  document.addEventListener('keyup', updateWordCountArea);
};
