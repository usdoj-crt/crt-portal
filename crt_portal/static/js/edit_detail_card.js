(function() {
  function makeToggleable(wrapper) {
    function showForm(form, info) {
      form.classList.remove('display-none');
      info.classList.add('display-none');
    }

    function hideForm(form, info) {
      form.classList.add('display-none');
      info.classList.remove('display-none');
    }

    function getFormState(form) {
      return [...form.elements].map(field => field.value).join(',');
    }

    function setButtonDisabled(form, saveButton, initialState) {
      // Save Button only enabled if form has been modified
      const currentState = getFormState(form);
      if (initialState === currentState) {
        saveButton.setAttribute('disabled', true);
      } else {
        saveButton.removeAttribute('disabled');
      }
    }

    function addFormUpdateEvents(form, saveButton) {
      // Generate listenable events for all form inputs, using `change` for IE11 support
      const initialState = getFormState(form);
      [...form.elements].forEach(function(field) {
        if (field.nodeName == 'INPUT') {
          field.addEventListener('input', () => setButtonDisabled(form, saveButton, initialState));
        } else if (field.nodeName == 'SELECT') {
          field.addEventListener('change', () => setButtonDisabled(form, saveButton, initialState));
        }
      });
    }

    const info = wrapper.querySelector('.toggle-info');
    const form = wrapper.querySelector('.toggle-edit-form');
    const saveButton = form.getElementsByTagName('button')[0];
    const cancelButton = form.getElementsByClassName('button--cancel')[0];
    const editButton = wrapper.querySelector('.edit-toggle-btn');

    addFormUpdateEvents(form, saveButton);
    cancelButton.addEventListener('click', () => hideForm(form, info));
    editButton.addEventListener('click', () => showForm(form, info));
  }

  document.querySelectorAll('.crt-toggleable-card').forEach(makeToggleable);
})();
