(function(root, dom) {
  root.CRT = root.CRT || {};

  function popField(array, field) {
    var index = array.indexOf(field);
    if (index > -1) {
      array.splice(index, 1);
    }
    return array;
  }

  function toggleFollowUpQuestions(event) {
    var selected = event.target.value;

    // For each key, show the listed fields and hide all others
    var allOptionalFields = [
      'public_or_private_employer',
      'employer_size',
      'election_details',
      'public_or_private_school',
      'inside_correctional_facility',
      'correctional_facility_type',
      'commercial_or_public_place',
      'other_commercial_or_public_place',
    ];

    var predicate_target_mapping = {
      workplace: ['public_or_private_employer', 'employer_size'],
      voting: ['election_details'],
      education: ['public_or_private_school'],
      police: ['inside_correctional_facility', 'correctional_facility_type'],
      commercial_or_public: ['commercial_or_public_place', 'other_commercial_or_public_place'],
    };

    // pick out and show dependent fields
    if (selected in predicate_target_mapping) {
      var show_these_fields = predicate_target_mapping[selected];
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

  // add listener
  var primary_issues = document.querySelector('#id_primary_complaint');
  primary_issues.addEventListener('change', toggleFollowUpQuestions);

  return root;
})(window, document);
