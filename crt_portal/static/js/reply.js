(function(root, dom) {
  root.CRT = root.CRT || {};

  document.addEventListener('DOMContentLoaded', function() {
    // `marked` should be loaded in global context at this point.
    if (marked) {
      marked.setOptions({
        gfm: true,
        breaks: true
      });
    } else {
      console.error('marked.js parser not loaded');
    }
  });

  function addReferralAddress(referral_contact) {
    const addressee = document.getElementById('form-letterhead--addressee');
    const deptAddressee = document.getElementById('form-letterhead--dept-addressee');

    if (deptAddressee) {
      deptAddressee.remove();
    }

    if (!addressee) return;

    const addressee_text = referral_contact?.addressee_text;
    if (!addressee_text) return;

    const newDeptAddressee = document.createElement('p');
    newDeptAddressee.id = 'form-letterhead--dept-addressee';
    newDeptAddressee.innerText = addressee_text;

    addressee.parentNode.insertBefore(newDeptAddressee, addressee);
  }

  root.CRT.renderTemplatePreview = function(
    modal,
    { reportId, responseTemplate, htmlBox, plaintextBox, afterRendered }
  ) {
    window
      .fetch(`/api/responses/${responseTemplate}/?report_id=${reportId}`)
      .then(response => response.json())
      .then(data => {
        if (data.is_html) {
          plaintextBox.hidden = true;
          htmlBox.hidden = false;
          htmlBox.innerHTML = marked.parse(data.body || '');
        } else {
          htmlBox.hidden = true;
          plaintextBox.hidden = false;
          plaintextBox.innerHTML = data.body || '';
        }
        addReferralAddress(data.referral_contact);
        if (afterRendered) afterRendered(data);
      });
  };

  root.CRT.handleReferral = async function(action, { reportId, responseTemplate, recipient }) {
    const response = await window.fetch('/api/response-action/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken')
      },
      mode: 'same-origin',
      body: JSON.stringify({
        action,
        report_id: reportId,
        template_id: responseTemplate,
        recipient
      })
    });
    const data = await response.json();
    return { data, status: response.status };
  };
})(window, document);
