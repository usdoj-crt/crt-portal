(function(root, dom) {
  function runNotebook(button) {
    const id = window.location.pathname.split('/notebook/')[1].split('/')[0];
    button.innerText = 'Running...';
    button.disabled = true;
    window.onbeforeunload = function() {
      return 'The Notebook is still running, are you sure you want to leave?';
    };
    runAllSteps(button, id, 0);
  }

  function runAllSteps(button, id, step) {
    if (step === null) {
      button.innerText = 'Done!';
      window.onbeforeunload = null;
      window.location.reload();
      return;
    }
    button.innerText = `Running Step ${step + 1}...`;
    window
      .fetch(`/analytics/refresh-notebook/${id}?run_only_cell=${step}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        mode: 'same-origin'
      })
      .then(response => response.json())
      .then(data => runAllSteps(button, id, data.next_cell))
      .catch(error => {
        button.innerText = `Failed on step ${step}`;
        console.error(`Failed on step ${step} - see network tab for failure content.`);
      });
  }

  function addListeners(button) {
    button.onclick = () => {
      runNotebook(button);
    };
    button.innerText = 'Re-run Notebook';
  }

  function setupButtons() {
    dom.querySelectorAll('.admin-run').forEach(addListeners);
  }

  root.addEventListener('load', setupButtons);
})(window, document);
