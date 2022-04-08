(function () {
  function showForm() {
    var showThese = document.querySelectorAll('.details-edit');
    var hideThese = document.querySelectorAll('.details');

    for (var i = 0; i < hideThese.length; i++) {
      hideThese[i].classList.add('display-none');
    }

    for (var i = 0; i < showThese.length; i++) {
      showThese[i].classList.remove('display-none');
    }

    // Show follow-up fields if any
    var primaryComplaint = document.getElementById('id_primary_complaint');
    showFollowUpQuestions(primaryComplaint.value);

    // reveal Buttons
    var buttons = detailsForm.getElementsByTagName('button');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].classList.remove('display-none');
    }
  }

  function hideForm() {
    var hideThese = document.querySelectorAll('.details-edit');
    var showThese = document.querySelectorAll('.details');

    for (var i = 0; i < hideThese.length; i++) {
      // This allows us to conditionally prevent hiding of elements
      // Such as the complaint summary field when there is none existing
      var element = hideThese[i];
      if (!element.classList.contains('always-display')) {
        element.classList.add('display-none');
      }
    }

    for (var i = 0; i < showThese.length; i++) {
      showThese[i].classList.remove('display-none');
    }

    // Hide Buttons
    var buttons = detailsForm.getElementsByTagName('button');
    for (var i = 0; i < buttons.length; i++) {
      var element = buttons[i];
      if (!element.classList.contains('always-display')) {
        element.classList.add('display-none');
      }
    }
  }

  function addShowFormHandler() {
    var editButton = document.getElementById('edit-details-btn');
    editButton.addEventListener('click', showForm);
  }

  function getFormState(form) {
    //  Serialize form values into a comma delimited string
    var serializedForm = new Array();
    for (var i = 0; i < form.elements.length; i++) {
      var field = form.elements[i];
      if (field.type != 'checkbox') {
        serializedForm.push(field.value);
      } else {
        serializedForm.push(field.checked);
      }
    }
    return serializedForm.join(',');
  }

  function setButtonDisabled() {
    // Save Button only enabled if form has been modified
    var currentState = getFormState(detailsForm);
    if (initialState === currentState) {
      saveButton.setAttribute('disabled', true);
    } else {
      saveButton.removeAttribute('disabled');
    }
  }

  function addFormUpdateEvents(form) {
    // Show follow-up fields if any
    var primaryComplaint = document.getElementById('id_primary_complaint');
    showFollowUpQuestions(primaryComplaint.value);

    // Generate listenable events for all form inputs, using `change` for IE11 support
    for (var i = 0; i < form.elements.length; i++) {
      var field = form.elements[i];
      if (field.nodeName == 'INPUT' || field.nodeName == 'TEXTAREA') {
        field.addEventListener('input', setButtonDisabled);
      } else if (field.nodeName == 'SELECT') {
        field.addEventListener('change', setButtonDisabled);
      }
    }
  }

  function popField(array, field) {
    var index = array.indexOf(field);
    if (index > -1) {
      array.splice(index, 1);
    }
    return array;
  }

  function showFollowUpQuestions(selectedReason) {
    var allOptionalFields = [
      'public_or_private_employer',
      'employer_size',
      'public_or_private_school',
      'inside_correctional_facility',
      'correctional_facility_type',
      'commercial_or_public_place',
      'other_commercial_or_public_place',
    ];

    var followupMapping = {
      workplace: ['public_or_private_employer', 'employer_size'],
      education: ['public_or_private_school'],
      police: ['inside_correctional_facility', 'correctional_facility_type'],
      commercial_or_public: ['commercial_or_public_place', 'other_commercial_or_public_place'],
    };

    // pick out and show dependent fields
    if (selectedReason in followupMapping) {
      var show_these_fields = followupMapping[selectedReason];
      for (i = 0; i < show_these_fields.length; i++) {
        var field = show_these_fields[i];
        var target_id = 'edit_id_' + show_these_fields[i];
        var target = document.getElementById(target_id);
        target.style.display = 'block';

        allOptionalFields = popField(allOptionalFields, field);
      }
    }

    // hide remaining fields
    for (i = 0; i < allOptionalFields.length; i++) {
      var target_id = 'edit_id_' + allOptionalFields[i];
      var target = document.getElementById(target_id);
      target.style.display = 'none';
    }
  }

  function toggleFollowUpQuestions(event) {
    showFollowUpQuestions(event.target.value);
  }

  var detailsInfo = document.getElementById('report-details');
  var detailsForm = document.getElementById('details-edit-form');
  var saveButton = detailsForm.getElementsByTagName('button')[0];
  var cancelButton = detailsForm.getElementsByClassName('button--cancel')[0];
  var primaryIssues = document.getElementById('id_primary_complaint');

  // add listeners
  primaryIssues.addEventListener('change', toggleFollowUpQuestions);
  cancelButton.addEventListener('click', hideForm);

  var initialState = getFormState(detailsForm);

  addFormUpdateEvents(detailsForm);
  addShowFormHandler();
})();
