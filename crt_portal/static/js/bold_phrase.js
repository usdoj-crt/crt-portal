(function() {
  var formGroup = document.getElementsByClassName('form-group')[0];
  var originalHelpText = formGroup.getElementsByClassName('help-text__small')[0];
  var phraseToBold = 'must be based'; // note: this will not apply any styling to translations unless translated phrases are added here
  var phraseIndex = originalHelpText.innerHTML.indexOf(phraseToBold);
  if (phraseIndex != -1) {
    var newHelpText = document.createElement('p');
    var newHelpTextMessage = originalHelpText.textContent.replace(
      phraseToBold,
      '<strong>' + phraseToBold + '</strong>'
    );
    newHelpText.classList.add('help-text__small');
    newHelpText.innerHTML = newHelpTextMessage;
    formGroup.replaceChild(newHelpText, originalHelpText);
  }
})();
