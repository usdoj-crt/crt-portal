var textAreaElem500 = document.getElementsByClassName("word-count-500");
var textAreaElem10 = document.getElementsByClassName("word-count-10");
var displayCountElem = document.getElementById("display_count");
var countMessageElem = document.getElementById("count_message");
var wordLimitAlert = document.getElementById("word-limit-alert");
var wordCountArea = document.getElementById("word_count_area");

// Show word count area for JS-enabled browsers:
if (wordCountArea) { wordCountArea.removeAttribute('hidden'); }

function updateWordCount (e, max='', textAreaElem='') {
    // Ignore `e` and read the value directly from the textarea here;
    // we want this function to work even if the user hasn't typed
    // anything (e.g. if textarea has initial content).
    var value = textAreaElem.value;
    var words = value ? value.match(/\S+/g).length : 0;

    displayCountElem.innerHTML = (max - words);

    if (words >= max) {
      // Word count greater than or equal to 500 word limit.
      // Trim the text down to the first 500 words:
      var trimmed = textAreaElem.value.split(" ", max).join(" ")
                                      .split("\t", max).join("\t")
                                      .split("\n", max).join("\n");
      textAreaElem.value = trimmed;

      // Update display for user:
      displayCountElem.innerHTML = '0';
      textAreaElem.classList.add('bg-gold-outline');
      wordLimitAlert.removeAttribute('hidden');
      wordLimitAlert.setAttribute('role', 'alert');
    } else {
      var wordsRemaining = max - words;
      displayCountElem.innerHTML = wordsRemaining;
      countMessageElem.value = (wordsRemaining === 1) ? 'word remaining' : 'words remaining';
      // textAreaElem.classList.remove('bg-gold-outline');
      wordLimitAlert.setAttribute('hidden', '');
      wordLimitAlert.removeAttribute('role');
    }

    if (words >= 400) {
      wordCountArea.setAttribute('aria-live', 'assertive');
    } else {
      wordCountArea.setAttribute('aria-live', 'polite');
    }
};


function listenWordCount (e){
  if (textAreaElem500.length > 0) {
    // Fire `updateWordCount()` on page load because textarea may have
    // some initial content; for example if the user fills in the textarea,
    // presses "Next" and then uses the back button to navigate back.
    // assuming only one per page
      updateWordCount(e, max=500, textAreaElem=document.getElementById(textAreaElem500[0].id));
  };
  if (textAreaElem10.length > 0) {
      updateWordCount(e, max=10, textAreaElem=document.getElementById(textAreaElem10[0].id));
  };
};

document.addEventListener('keyup', listenWordCount);


function checkOther(elem){
  var checkBox = document.querySelectorAll('.' + 'usa-checkbox__input').item(13);
  var otherArea = document.getElementById("other-class-option");
  if (checkBox.checked == true){
    otherArea.removeAttribute('hidden');
  } else {
    otherArea.setAttribute('hidden', '');
  }
}
