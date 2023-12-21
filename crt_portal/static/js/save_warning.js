(function() {
  let showWarning = false;
  const commentForm = document.querySelector('#comment-actions-comment');
  commentForm.addEventListener('change', () => (showWarning = true));
  const actionForm = document.querySelector('#complaint-view-actions');
  actionForm
    .querySelectorAll('input')
    .forEach(input => input.addEventListener('change', () => (showWarning = true)));
  actionForm
    .querySelectorAll('select')
    .forEach(input => input.addEventListener('change', () => (showWarning = true)));
  const contactForm = document.querySelector('#contact-edit-form');
  contactForm.addEventListener('change', () => (showWarning = true));
  const detailsForm = document.querySelector('#details-edit-form');
  detailsForm.addEventListener('change', () => (showWarning = true));
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
