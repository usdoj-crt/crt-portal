(function(root, dom) {
  root.CRT = root.CRT || {};

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
})(window, document);
