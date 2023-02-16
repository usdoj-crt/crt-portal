(function(root, dom) {
  function getCWs(targets, reports) {
    for (const [id, report] of Object.entries(reports.reports)) {
      if (!report.constant_writer) continue;
      const target = Array.from(targets).find(target => target.getAttribute('data-id') === id);
      target.classList.remove('hidden');
    }
  }

  function makeQuery() {
    const targets = dom.querySelectorAll('.show-cw');
    const report_objects = {};
    targets.forEach(target => {
      report_objects[target.dataset.id] = target.getAttribute('data-email');
    });
    window
      .fetch(`/api/report-cws/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        mode: 'same-origin',
        body: `${JSON.stringify(report_objects)}`
      })
      .then(response => response.json().then(reports => getCWs(targets, reports)))
      .catch(error => {
        console.log(error);
      });
  }

  root.addEventListener('load', makeQuery);
})(window, document);
