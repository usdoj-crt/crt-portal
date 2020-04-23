(function() {

    function showContactForm() {
      contactForm.classList.remove('display-none');
      contactInfo.classList.add('display-none');
    }

    function hideContactForm() {
      contactForm.classList.add('display-none');
      contactInfo.classList.remove('display-none');
    }

    function addShowFormHandler() {
      var editButton = document.getElementById('edit-contact-info-btn');
      editButton.addEventListener('click', showContactForm);
    }

    function setButtonDisabled() {
      // Save Button only enabled if form has been modified
      var currentState = Array.from(new FormData(contactForm),e => e[1]).join(',');
      if (initialState === currentState) {
        saveButton.setAttribute('disabled', true);
      }
      else {
        saveButton.removeAttribute('disabled')
      }
    }

    var contactInfo = document.getElementById('contact-info');
    var contactForm = document.getElementById('contact-edit-form');
    var saveButton = contactForm.getElementsByTagName('button')[0];
    var cancelButton = contactForm.getElementsByClassName('button--cancel')[0];

    var initialState = Array.from(new FormData(contactForm),e => e[1]).join(',')

    contactForm.addEventListener('input', setButtonDisabled);

    saveButton.addEventListener('click', hideContactForm);
    cancelButton.addEventListener('click', hideContactForm);

    addShowFormHandler();
  })();
