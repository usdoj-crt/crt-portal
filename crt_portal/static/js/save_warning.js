(function() {
    let formChanged = false;
    const statusForm = document.querySelector("#complaint-view-actions");
    statusForm.addEventListener('change', () => formChanged = true);
    window.addEventListener('beforeunload', (e) => {
      if (formChanged) {
        e.returnValue = 'Changes you made may not be saved.';
      }
    });
  })();