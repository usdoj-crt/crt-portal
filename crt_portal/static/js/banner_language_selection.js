(function(root, dom) {
  var buttons = document.querySelectorAll('.language-selection__button');
  buttons.forEach(function(button) {
    button.onclick = function(event) {
      console.log('handling button click');
      event.preventDefault();

      var language_code = this.getAttribute('data-value');
      console.log(language_code);

      var language_input_el = document.getElementById('language_input');

      language_input_el.setAttribute('value', language_code);

      var form = document.getElementById('language_selection_form');
      form.submit();
    };
  });
})(window, document);
