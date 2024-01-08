(function() {
  let showWarning = false;
  const maybeAddWarning = function(e) {
    if (
      e.target.classList.contains('usa-combo-box__select') &&
      !e.target.classList.contains('combobox-loaded')
    ) {
      e.target.classList.add('combobox-loaded');
    } else {
      showWarning = true;
    }
  };

  const commentForm = document.querySelector('#comment-actions-comment');
  commentForm.addEventListener('change', maybeAddWarning);
  const actionForm = document.querySelector('#complaint-view-actions');
  actionForm
    .querySelectorAll('input')
    .forEach(input => input.addEventListener('change', maybeAddWarning));
  actionForm
    .querySelectorAll('select')
    .forEach(select => select.addEventListener('change', maybeAddWarning));
  const contactForm = document.querySelector('#contact-edit-form');
  contactForm.addEventListener('change', maybeAddWarning);
  const detailsForm = document.querySelector('#details-edit-form');
  detailsForm.addEventListener('change', maybeAddWarning);
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
