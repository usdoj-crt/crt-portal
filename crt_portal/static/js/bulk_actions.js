(function(root, dom) {
  accessibleAutocomplete.enhanceSelectElement({
    defaultValue: '',
    selectElement: document.querySelector('#id_assigned_to'),
    onConfirm: function(what) {
      var buttons = document.querySelectorAll('.complaint-page .usa-button');
      for (var i = 0; i < buttons.length; i++) {
        var button = buttons[i];
        button.removeAttribute('disabled');
      }
      // work around a bug in the accessible autocomplete library
      var actualSelectElement = document.getElementById('id_assigned_to-select');
      var options = actualSelectElement.options;
      for (var i = 0; i < options.length; i++) {
        var option = options[i];
        if (option.text === what) {
          actualSelectElement.value = option.value;
          break;
        }
      }
    }
  });

  var assign_section = document.getElementById('assign_section');
  var warning_section = document.getElementById('warning_section');
  var warning_count_partial = document.getElementById('warning_count_partial');
  var warning_count_all = document.getElementById('warning_count_all');
  var confirm_button = document.getElementById('confirm_button');

  var update_warning = function(is_partial) {
    var assignee = document.getElementById('warning_section_assignee');
    var actualSelectElement = document.getElementById('id_assigned_to-select');
    assign_section.setAttribute('hidden', 'hidden');
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
    // work around a bug: if user removes an auto complete field, the
    // selected item is still present, so pull from the actual selection
    var index = actualSelectElement.selectedIndex;
    assignee.innerText = actualSelectElement.options[index].text;
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
      assign_section.removeAttribute('hidden');
      warning_section.setAttribute('hidden', 'hidden');
    };
  }
})(window, document);
