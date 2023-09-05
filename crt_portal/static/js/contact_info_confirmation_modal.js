(function(root) {
  // note that modal.js must be loaded beforehand
  var modal_el = document.getElementById('contact-info-confirmation--modal');

  function clickSubmit(stepOneSubmitButton) {
    stepOneSubmitButton.addEventListener('click', event => {
      var phone_el = document.getElementsByName('0-contact_phone')[0];
      var email_el = document.getElementsByName('0-contact_email')[0];
      var requiredFieldSelected =
        document.getElementsByName('0-servicemember')[0].checked ||
        document.getElementsByName('0-servicemember')[1].checked;
      var noContactInfo = !phone_el.value && !email_el.value;

      // If there is contact information OR if the required field is not filled out, no modal is needed
      if (!noContactInfo || !requiredFieldSelected) {
        event.preventDefault();
        submitNextButton.click();
      } else {
        event.preventDefault();
        const cancelModalButton = modal_el.querySelector('.external-link--cancel');

        // field_el is the field element that will need to be filled out.  We want to focus that field and scroll to it.
        var field_el = {};
        if (noContactInfo || !email_el.value) {
          field_el = email_el;
        } else if (!phone_el.value) {
          field_el = phone_el;
        }
        root.CRT.cancelModal(modal_el, cancelModalButton, field_el);
        root.CRT.openModal(modal_el);
      }
    });
  }

  if (root.CRT.stageNumber === 1) {
    var stepOneSubmitButton = document.getElementById('report-step-1-continue');
    if (stepOneSubmitButton) {
      var submitNextButton = document.getElementById('submit-next');
      var continue_modal_button = modal_el.querySelector('.external-link--continue');
      continue_modal_button.onclick = function(event) {
        event.preventDefault();
        submitNextButton.click();
      };
      clickSubmit(stepOneSubmitButton);
    }
  }
})(window);
