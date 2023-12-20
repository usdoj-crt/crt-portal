(function() {
  let showWarning = false;
  const forms = document.querySelectorAll('.usa-form');
  forms.forEach(form => {
    form.addEventListener('change', () => (showWarning = true));
  });
  const btns = document.querySelectorAll('[type="submit"]');
  btns.forEach(btn => {
    btn.addEventListener('click', () => (showWarning = false));
  });
  window.addEventListener('beforeunload', e => {
    if (showWarning) {
      e.returnValue = 'Changes you made may not be saved.';
    }
  });
})();
