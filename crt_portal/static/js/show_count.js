(function(root, dom) {
  function updateCount(target, summary) {
    const count = summary.report_count;
    const span = document.createElement('span');
    span.className = 'added-count';
    span.appendChild(document.createTextNode(`(${count})`));
    target.appendChild(span);
  }

  function makeQuery(target) {
    const params = target.dataset.countParams;
    window
      .fetch(`/api/report-summary/${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        mode: 'same-origin'
      })
      .then(response => response.json().then(summary => updateCount(target, summary)))
      .catch(error => {
        console.error(error);
      });
  }

  function makeQueries() {
    const targets = dom.querySelectorAll('.show-count');
    targets.forEach(makeQuery);
  }

  root.addEventListener('load', makeQueries);
})(window, document);
