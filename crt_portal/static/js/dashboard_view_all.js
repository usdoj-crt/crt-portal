(function(root, dom) {
  function toggleTarget(toggle) {
    const arrow = toggle.querySelector('.icon');
    const id = toggle.dataset['id'];
    const summary = dom.getElementById(`tr-additional-${id}`);
    toggle.setAttribute('aria-expanded', isToggled(toggle) ? 'false' : 'true');
    arrow.classList.toggle('rotate');
    summary.toggleAttribute('hidden');
  }

  function isToggled(target) {
    return target.getAttribute('aria-expanded') === 'true';
  }

  function markAsViewed(ids) {
    if (!ids.length) return;
    window.onbeforeunload = function() {
      return 'Report views have not yet saved, are you sure you want to leave?';
    };
    window
      .fetch(`/api/reports/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        mode: 'same-origin',
        body: JSON.stringify({ report_pks: ids })
      })
      .then(() => (window.onbeforeunload = null))
      .catch(error => {
        console.error(error);
      });
  }

  function addToggleListener(toggleAll, parentTable) {
    toggleAll.addEventListener('click', event => {
      event.preventDefault();
      const allToggled = isToggled(toggleAll);
      toggleAll.querySelector('.icon').classList.toggle('rotate');
      toggleAll.setAttribute('aria-expanded', allToggled ? 'false' : 'true');
      const toggles = [...parentTable.querySelectorAll('a.td-toggle')].filter(
        toggle => isToggled(toggle) == allToggled
      );

      toggles.forEach(toggle => toggleTarget(toggle));

      if (allToggled || toggleAll.dataset['posted'] === 'true') return;

      markAsViewed(toggles.map(toggle => Number(toggle.dataset['id'])));
      // Set a flag on the toggle so we don't resubmit data multiple times per session.
      toggleAll.dataset['posted'] = 'true';
    });
  }

  const toggleAllButtons = dom.querySelectorAll('.td-toggle-all');
  toggleAllButtons.forEach(toggleAll => {
    const parentTable = toggleAll.closest('.usa-table.crt-table');
    addToggleListener(toggleAll, parentTable);
  });
})(window, document);
