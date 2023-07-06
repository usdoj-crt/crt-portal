(function(root) {
  const actionButtons = document.querySelectorAll('.action_button');
  const report_id = document.getElementById('report-id').value;
  const template_id = document.getElementById('template-id').value;
  function getReferralResponse(e) {
    e.preventDefault();
    window
      .fetch('/api/referral-response/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        mode: 'same-origin',
        body: JSON.stringify({ report_id, template_id, action: e.target.innerText.toLowerCase() })
      })
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        console.log(data);
      })
      .catch(error => {
        console.error(error);
      });
  }
  actionButtons.forEach(button => button.addEventListener('click', getReferralResponse));
})(window);
