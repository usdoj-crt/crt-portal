function announce(element) {
    var submitButtons = {
      'submit-summary': 'Summary submitted',
      'submit-comment': 'Comment updated',
      'submit-apply-changes': 'Updated activity',
    }
    var message = submitButtons[element.id];
    console.log(message)

    let statusAlert = document.createElement("p");
    statusAlert.setAttribute("role", "alert");
    let messageText = document.createTextNode(message);
    statusAlert.appendChild(messageText);
    document.body.appendChild(statusAlert);
}

var submit_buttons = document.querySelectorAll('*[id^="submit-"]');
submit_buttons.forEach(function(button) {
    button.addEventListener('click', () => {
     announce(button);
    });
    // I would have thought this was necessary but leads to duplicates
    // button.addEventListener('keydown', (event) => {
    //   if (event.code === 'Space' || event.code === 'Enter') {
    //     announce(button);
    //   }
    // });
});
