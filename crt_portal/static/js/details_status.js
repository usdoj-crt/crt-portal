// Announces changes when a user clicks a submit button on the CRT details page
function announce(element) {
  var submitButtons = {
    'submit-summary': 'Summary submitted',
    'submit-comment': 'Comment updated',
    'submit-apply-changes': 'Updated activity'
  };
  var message = submitButtons[element.id];

  let statusAlert = document.createElement('p');
  statusAlert.setAttribute('role', 'alert');
  let alertText = document.createTextNode(message);
  statusAlert.appendChild(alertText);
  document.body.appendChild(statusAlert);
}

var submit_buttons = document.querySelectorAll('*[id^="submit-"]');
submit_buttons.forEach(function(button) {
  button.addEventListener('click', () => {
    announce(button);
  });
});
