/** Used by public and internal-facing forms to prevent duplicate submission. */
(function(root) {
  function disableButtons(form) {
    // Use setTimeout to detach from the submission thread, ensuring the form is
    // submitted before we disable the buttons.
    const submitButtons = form.querySelectorAll('[type="submit"]');
    setTimeout(() => {
      submitButtons.forEach(button => {
        button.disabled = true;
      });
    }, 0);
  }

  root.addEventListener('load', () => {
    Array.from(document.forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (form.classList.contains('is-submitting')) {
          console.warn('Preventing duplicate submission');
          event.preventDefault();
          return false;
        }
        form.classList.add('is-submitting');
        disableButtons(form);
        return true;
      });
    });
  });
})(window);
