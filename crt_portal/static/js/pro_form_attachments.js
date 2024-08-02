(function(root) {
  const addAttachmentEl = document.getElementById('add_attachment');
  const fileEl = document.getElementById('file_input');
  const responseWrapper = document.getElementsByClassName('response-wrapper')[0];
  const attachmentInput = document.getElementById('pro_form_attachment');
  const downloadLinks = document.querySelectorAll('.download-attachment');
  downloadLinks.forEach(downloadLink => {
    downloadLink.onclick = function(event) {
      event.preventDefault();
      downloadAttachment(event);
    };
  });
  const removeLinks = document.querySelectorAll('.remove-attachment-button');
  removeLinks.forEach(removeLink => {
    removeLink.onclick = function(event) {
      event.preventDefault();
      removeFile(event);
    };
  });
  const violationSummary = document.querySelector('#id_0-violation_summary');
  addAttachmentEl.onclick = function(event) {
    event.preventDefault();
    fileEl.click();
  };

  fileEl.onchange = function(event) {
    const modal = document.getElementById('attachment-uploading--modal');
    root.CRT.openModal(modal);
    addAttachment(event, modal);
  };

  function removeFile(event) {
    event.preventDefault();

    const attachmentId = event.target.getAttribute('data-attachment-id');
    const attachmentFilename = event.target.getAttribute('data-attachment-filename');

    const modal = document.getElementById('attachment-removal-confirmation--modal');
    const filenameEl = document.getElementById('attachment-removal--filename');
    const noBtn = document.getElementById('attachment-removal--no');
    const yesBtn = document.getElementById('attachment-removal--yes');

    filenameEl.innerText = attachmentFilename;
    noBtn.onclick = function(event) {
      event.preventDefault();
      root.CRT.closeModal(modal);
    };
    yesBtn.onclick = function(event) {
      event.preventDefault();

      removeAttachment(attachmentId);
      root.CRT.closeModal(modal);
    };

    root.CRT.openModal(modal);
  }

  function downloadAttachment(e) {
    const attachmentId = e.target.getAttribute('data-attachment-id');
    window
      .fetch(`/api/proform-attachment-action/?attachment_id=${attachmentId}`, {
        method: 'GET',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        responseType: 'blob',
        mode: 'same-origin'
      })
      .then(function(response) {
        if (response.status != 404) {
          const url = response.url;
          window.open(url, '_blank');
        }
        responseWrapper.innerHTML =
          response.status == 404
            ? `<div class="usa-alert__body"><em class="usa-alert__text">File not found</em></div>`
            : '';
        responseWrapper.hidden = response.status != 404;
      })
      .catch(error => {
        console.error(error);
      });
  }

  function createRow(data) {
    const attachmentTable = document.getElementById('attachmentTable');
    const newRow = document.createElement('tr');
    newRow.id = data.id + 'row';
    newRow.innerHTML = `
            <td>
                <a href="#" data-attachment-id="${data.id}" class="download-attachment"> ${data.name}</a>
            </td>
            <td>
                <button data-attachment-id="${data.id}" data-attachment-filename="${data.name}" class="usa-button usa-button--outline remove-attachment-button">
                <img data-attachment-id="${data.id}" src="/static/img/trash-2.svg" alt="remove attachment" class="icon"></button>
            </td>
            `;
    attachmentTable.appendChild(newRow);
    const downloadLink = newRow.querySelector('a');
    downloadLink.onclick = function(event) {
      event.preventDefault();
      downloadAttachment(event);
    };
    const removeLink = newRow.querySelector('button');
    removeLink.onclick = function(event) {
      event.preventDefault();
      removeFile(event);
    };
    violationSummary.value = 'See attachment.';
    if (attachmentInput.value == 'None') {
      attachmentInput.value = data.id + ',';
    } else {
      attachmentInput.value += data.id + ',';
    }
  }

  function removeAttachment(attachmentId) {
    const csrf = Cookies.get('csrftoken');
    let formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrf);
    formData.append('action', 'removed');
    formData.append('attachment_id', attachmentId);
    window
      .fetch('/api/proform-attachment-action/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrf
        },
        mode: 'same-origin',
        body: formData
      })
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        const row = document.getElementById(`${data.id}row`);
        if (row) {
          row.remove();
        }
        responseWrapper.innerHTML =
          data.type == 'error'
            ? `<div class="usa-alert__body"><em class="usa-alert__text">${data.response}</em></div>`
            : '';
        responseWrapper.hidden = data.type != 'error';
        const attachmentInputVal = attachmentInput.value;
        const regex = new RegExp(data.id + ',');
        const newVal = attachmentInputVal.replace(regex, '');
        attachmentInput.value = newVal;
      })
      .catch(error => {
        console.error(error);
      });
  }

  function addAttachment(e, modal) {
    e.preventDefault();
    const csrf = Cookies.get('csrftoken');
    let formData = new FormData();
    const file = e.target.files[0];
    formData.append('file', file);
    formData.append('csrfmiddlewaretoken', csrf);
    formData.append('action', 'added');
    window
      .fetch('/api/proform-attachment-action/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrf
        },
        mode: 'same-origin',
        body: formData
      })
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        responseWrapper.innerHTML =
          data.type == 'error'
            ? `<div class="usa-alert__body"><em class="usa-alert__text">${data.response}</em></div>`
            : '';
        responseWrapper.hidden = data.type != 'error';
        if (data.id) {
          createRow(data);
        }
      })
      .catch(error => {
        console.error(error);
      });
    root.CRT.closeModal(modal);
  }
})(window);
