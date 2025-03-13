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
    // Pull all formData out into a JS object
    // Specific check to handle the tags field as that has special logic
    // See usa_tag_select.html and usa_tag_select.js
    const formData = {};
    [...form.elements].forEach(field => {
      if (field.name == 'tags') {
        if (!Object.hasOwn(formData, 'tags')) {
          formData[field.name] = [];
        }
        formData[field.name].push(field.checked);
      } else {
        if (field.type == 'checkbox') {
          formData[field.name] = field.checked;
        } else {
          formData[field.name] = field.value;
        }
      }
    });
    return formData;
  }

  function hasFormStateChanged() {
    // Check the current form state against the initial form state
    // We want to check for Arrays specifically so we can sort them
    // ensuring the values are the same regardless of order.
    const currentState = getFormState(detailsForm);
    for (const [key, value] of Object.entries(currentState)) {
      if (Array.isArray(value)) {
        const initialArray = initialState[key].slice().sort();
        if (value.length != initialArray.length) {
          return true;
        }
        const currentValueArray = value.slice().sort();
        for (let i = 0; i < currentValueArray.length; i++) {
          if (currentValueArray[i] !== initialArray[i]) {
            return true;
          }
        }
      } else {
        if (value !== initialState[key]) {
          return true;
        }
      }
    }
    return false;
  }

  function setButtonDisabled() {
    // Save Button only enabled if form has been modified
    if (!hasFormStateChanged()) {
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
        field.addEventListener('change', () => {
          // Add a timeout here because sometimes setButtonDisabled was being called
          // before the value actually updated in the field, resulting in incorrect state
          setTimeout(() => {
            setButtonDisabled(field);
          });
        });
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
    let allOptionalFields = [
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
  const saveButton = detailsForm.getElementsByClassName('button--save')[0];
  const cancelButton = detailsForm.getElementsByClassName('button--cancel')[0];
  const primaryIssues = document.getElementById('id_primary_complaint');

  // add listeners
  primaryIssues.addEventListener('change', toggleFollowUpQuestions);
  cancelButton.addEventListener('click', () => hideForm(detailsForm));

  const initialState = getFormState(detailsForm);
  console.log('EditDetails: InitialState = ', initialState);

  addFormUpdateEvents(detailsForm);
  addShowFormHandler(detailsForm);
})();
