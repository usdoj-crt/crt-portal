(function(root, dom) {
  var buttons = document.querySelectorAll('.language-selection__button');
  for (var index in buttons) {
    var button = buttons[index];
    button.onclick = function(event) {
      event.preventDefault();

      var language_code = this.getAttribute('data-value');

      var language_input_el = document.getElementById('language_input');

      language_input_el.setAttribute('value', language_code);

      var form = document.getElementById('language_selection_form');
      form.submit();
    };
  }
})(window, document);
