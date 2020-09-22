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
  var show_warning_section = document.getElementById('show_warning_section');
  show_warning_section.onclick = function(event) {
    event.preventDefault();
    var assignee = document.getElementById('warning_section_assignee');
    var actualSelectElement = document.getElementById('id_assigned_to-select');
    assign_section.setAttribute('hidden', 'hidden');
    warning_section.removeAttribute('hidden');
    // work around a bug: if user removes an auto complete field, the
    // selected item is still present, so pull from the actual selection
    var index = actualSelectElement.selectedIndex;
    assignee.innerText = actualSelectElement.options[index].text;
  };

  var cancel_warning_section = document.getElementById('cancel_warning_section');
  cancel_warning_section.onclick = function(event) {
    event.preventDefault();
    assign_section.removeAttribute('hidden');
    warning_section.setAttribute('hidden', 'hidden');
  };
})(window, document);
