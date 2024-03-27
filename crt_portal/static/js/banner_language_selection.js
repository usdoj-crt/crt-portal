(function(root, dom) {
  const buttons = document.querySelectorAll('.language-selection__button');
  buttons.forEach(button => {
    button.onclick = function(event) {
      event.preventDefault();

      const language_code = this.getAttribute('data-value');

      const language_input_el = document.getElementById('language_input');

      language_input_el.setAttribute('value', language_code);

      const url = new URL(window.location.href);
      url.searchParams.set('lang', language_code);
      window.history.replaceState({}, '', url);

      const form = document.getElementById('language_selection_form');
      form.submit();
    };
  });
})(window, document);
