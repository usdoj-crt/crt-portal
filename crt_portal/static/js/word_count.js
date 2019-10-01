var textAreaElem = document.getElementById("id_1-violation_summary");
var displayCountElem = document.getElementById("display_count");
var countMessageElem = document.getElementById("count_message");

function updateWordCount (event) {
    var value = event ? event.target.value : '';
    var words = value ? value.match(/\S+/g).length : 0;

    displayCountElem.innerHTML = (500 - words);

    if (words > 500) {
      // Split the string on first 500 words and rejoin on spaces
      var trimmed = textAreaElem.value.split(/\s+/, 500).join(" ");
      // replace the input with trimmed text
      textAreaElem.value = trimmed;
      countMessageElem.innerHTML = ' word limit reached';
      displayCountElem.innerHTML = '500';
    } else {
      displayCountElem.innerHTML =  (500 - words);
      countMessageElem.innerHTML = ' word(s) remaining'
    }
};

if (textAreaElem) {
  updateWordCount();

  document.addEventListener('keyup', updateWordCount);
};

