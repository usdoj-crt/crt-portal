(function(root, dom) {
  root.CRT = root.CRT || {};

  function toggleFollowUpQuestions(event) {
    var primary_complaint_id = event.target.id
    var predicate_target_mapping = {
     'id_0-primary_complaint_0': ['div-id_0-public_or_private_employer_0', 'div-id_0-employer_size_0'],
     'id_0-primary_complaint_2': ['div-id_0-public_or_private_school_0'],
     'id_0-primary_complaint_4': ['div-id_0-inside_correctional_facility_0', 'div-id_0-correctional_facility_type_0'],
     'id_0-primary_complaint_5': ['div-id_0-commercial_or_public_place_0', 'div-id_0-other_commercial_or_public_place']
    }
    // show
    if(primary_complaint_id in predicate_target_mapping){
      var targets = predicate_target_mapping[primary_complaint_id]
      targets.forEach(function(question_id){
        var target = document.getElementById(question_id)
        target.style.display = 'block'
      })
    }
    // hide
    Object.keys(predicate_target_mapping).forEach(function(primary_id){
      if(primary_complaint_id != primary_id){
        var targets = predicate_target_mapping[primary_id]
        targets.forEach(function(question_id){
          var target = document.getElementById(question_id)
          target.style.display = 'none'
        })
      }
    })
  };

  // add listeners
  var primary_issues = document.querySelectorAll('*[id^="id_0-primary_complaint_"]');
  primary_issues.forEach(function(radio_element){
    radio_element.addEventListener('click', toggleFollowUpQuestions);
  })

  return root;
})(window, document);
