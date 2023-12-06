(function() {
  function showForm(detailsForm) {
    detailsForm.classList.add('details-form-edit');
    detailsForm.classList.remove('details-form-view');
    const showThese = document.querySelectorAll('.details-edit');
    const hideThese = document.querySelectorAll('.details');

    hideThese.forEach(toHide => {
      toHide.classList.add('display-none');
    });

    showThese.forEach(toShow => {
      toShow.classList.remove('display-none');
    });

    // Show follow-up fields if any
    const primaryComplaint = document.getElementById('id_primary_complaint');
    showFollowUpQuestions(primaryComplaint.value);

    // reveal Buttons
    const buttons = detailsForm.getElementsByTagName('button');
    [...buttons].forEach(button => {
      button.classList.remove('display-none');
    });
  }

  function hideForm(detailsForm) {
    detailsForm.classList.add('details-form-view');
    detailsForm.classList.remove('details-form-edit');
    const hideThese = document.querySelectorAll('.details-edit');
    const showThese = document.querySelectorAll('.details');

    hideThese.forEach(toHide => {
      // This allows us to conditionally prevent hiding of elements
      // Such as the complaint summary field when there is none existing
      if (!toHide.classList.contains('always-display')) {
        toHide.classList.add('display-none');
      }
    });

    showThese.forEach(toShow => {
      toShow.classList.remove('display-none');
    });

    // Hide Buttons
    const buttons = detailsForm.getElementsByTagName('button');
    [...buttons].forEach(button => {
      if (!button.classList.contains('always-display')) {
        button.classList.add('display-none');
      }
    });
  }

  function addShowFormHandler(detailsForm) {
    const editButton = document.getElementById('edit-details-btn');
    editButton.addEventListener('click', () => showForm(detailsForm));
  }

  function getFormState(form) {
    //  Serialize form values into a comma delimited string
    const serializedForm = new Array();
    [...form.elements].forEach(field => {
      if (field.type != 'checkbox') {
        serializedForm.push(field.value);
      } else {
        serializedForm.push(field.checked);
      }
    });
    return serializedForm.join(',');
  }

  function setButtonDisabled() {
    // Save Button only enabled if form has been modified
    const currentState = getFormState(detailsForm);
    if (initialState === currentState) {
      saveButton.setAttribute('disabled', true);
    } else {
      saveButton.removeAttribute('disabled');
    }
  }

  function addFormUpdateEvents(form) {
    // Show follow-up fields if any
    const primaryComplaint = document.getElementById('id_primary_complaint');
    showFollowUpQuestions(primaryComplaint.value);

    // Generate listenable events for all form inputs, using `change` for IE11 support
    [...form.elements].forEach(field => {
      if (field.nodeName == 'INPUT' || field.nodeName == 'TEXTAREA') {
        field.addEventListener('input', setButtonDisabled);
      } else if (field.nodeName == 'SELECT') {
        field.addEventListener('change', setButtonDisabled);
      }
    });
  }

  function popField(array, field) {
    const index = array.indexOf(field);
    if (index > -1) {
      array.splice(index, 1);
    }
    return array;
  }

  function showFollowUpQuestions(selectedReason) {
    const allOptionalFields = [
      'public_or_private_employer',
      'employer_size',
      'public_or_private_school',
      'inside_correctional_facility',
      'correctional_facility_type',
      'commercial_or_public_place',
      'other_commercial_or_public_place'
    ];

    const followupMapping = {
      workplace: ['public_or_private_employer', 'employer_size'],
      education: ['public_or_private_school'],
      police: ['inside_correctional_facility', 'correctional_facility_type'],
      commercial_or_public: ['commercial_or_public_place', 'other_commercial_or_public_place']
    };

    // pick out and show dependent fields
    if (selectedReason in followupMapping) {
      const showTheseFields = followupMapping[selectedReason];
      showTheseFields.forEach(field => {
        const target = document.getElementById('edit_id_' + field);
        target.style.display = 'block';

        allOptionalFields = popField(allOptionalFields, field);
      });
    }

    // hide remaining fields
    allOptionalFields.forEach(field => {
      const target = document.getElementById('edit_id_' + field);
      target.style.display = 'none';
    });
  }

  function toggleFollowUpQuestions(event) {
    showFollowUpQuestions(event.target.value);
  }

  const detailsForm = document.getElementById('details-edit-form');
  const saveButton = detailsForm.getElementsByTagName('button')[0];
  const cancelButton = detailsForm.getElementsByClassName('button--cancel')[0];
  const primaryIssues = document.getElementById('id_primary_complaint');

  // add listeners
  primaryIssues.addEventListener('change', toggleFollowUpQuestions);
  cancelButton.addEventListener('click', () => hideForm(detailsForm));

  const initialState = getFormState(detailsForm);

  addFormUpdateEvents(detailsForm);
  addShowFormHandler(detailsForm);
})();
