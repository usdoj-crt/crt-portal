(function(root, dom) {
  function toggleTarget(toggle) {
    const arrow = toggle.querySelector('.icon');
    const id = toggle.dataset['id'];
    const summary = dom.getElementById(`tr-additional-${id}`);
    arrow.classList.toggle('rotate');
    summary.toggleAttribute('hidden');
  }

  function isToggled(target) {
    return target.querySelector('.icon').classList.contains('rotate');
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

  const toggleAll = dom.querySelector('a.td-toggle-all');
  toggleAll.onclick = function(event) {
    event.preventDefault();
    const allToggled = isToggled(toggleAll);
    toggleAll.querySelector('.icon').classList.toggle('rotate');
    const toggles = [...dom.querySelectorAll('a.td-toggle')].filter(
      toggle => isToggled(toggle) == allToggled
    );

    toggles.forEach(toggle => toggleTarget(toggle));

    if (allToggled || toggleAll.dataset['posted'] === 'true') return;

    markAsViewed(toggles.map(toggle => Number(toggle.dataset['id'])));
    // Set a flag on the toggle so we don't resubmit data multiple times per session.
    toggleAll.dataset['posted'] = 'true';
  };
})(window, document);
