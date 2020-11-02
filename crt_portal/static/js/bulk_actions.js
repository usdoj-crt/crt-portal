(function(root, dom) {
  // TODO: '#id_assigned_to'

  var comment_field = document.getElementById('id_comment');
  comment_field.oninput = function(event) {
    var buttons = document.querySelectorAll('.complaint-page .usa-button');
    for (var i = 0; i < buttons.length; i++) {
      var button = buttons[i];
      if (event.target.value) {
        button.removeAttribute('disabled');
      } else {
        button.setAttribute('disabled', 'disabled');
      }
    }
  };

  var actions_section = document.getElementById('bulk_actions_section');
  var warning_section = document.getElementById('warning_section');
  var warning_count_partial = document.getElementById('warning_count_partial');
  var warning_count_all = document.getElementById('warning_count_all');
  var confirm_button = document.getElementById('confirm_button');

  var update_warning = function(is_partial) {
    actions_section.setAttribute('hidden', 'hidden');
    warning_section.removeAttribute('hidden');
    if (is_partial) {
      warning_count_all.setAttribute('hidden', 'hidden');
      warning_count_partial.removeAttribute('hidden');
      confirm_button.setAttribute('value', 'none');
    } else {
      warning_count_all.removeAttribute('hidden');
      warning_count_partial.setAttribute('hidden', 'hidden');
      confirm_button.setAttribute('value', 'confirm_all');
    }
  };

  var show_warning_section = document.getElementById('show_warning_section');
  if (show_warning_section) {
    show_warning_section.onclick = function(event) {
      event.preventDefault();
      update_warning(false);
    };
  }

  var show_warning_section_partial = document.getElementById('show_warning_section_partial');
  if (show_warning_section_partial) {
    show_warning_section_partial.onclick = function(event) {
      event.preventDefault();
      update_warning(true);
    };
  }

  var cancel_warning_section = document.getElementById('cancel_warning_section');
  if (cancel_warning_section) {
    cancel_warning_section.onclick = function(event) {
      event.preventDefault();
      actions_section.removeAttribute('hidden');
      warning_section.setAttribute('hidden', 'hidden');
    };
  }

  var assigned_section = document.getElementById('id_assigned_section');
  var original_statute_value = document.getElementById('id_primary_statute').value;
  assigned_section.onchange = function(event) {
    var status = document.getElementById('id_status');
    status.value = 'new';
    status.setAttribute('disabled', 'disabled');
    var primaryStatute = document.getElementById('id_primary_statute');
    primaryStatute.value = original_statute_value;
    primaryStatute.setAttribute('disabled', 'disabled');
    var selectElement = document.getElementById('id_assigned_to');
    selectElement.value = '';
    selectElement.setAttribute('disabled', 'disabled');
    var actualSelectElement = document.getElementById('id_assigned_to-select');
    actualSelectElement.value = '';
  };

  // disable "Multiple" selection for section
  assigned_section.options[0].setAttribute('disabled', 'disabled');
})(window, document);
