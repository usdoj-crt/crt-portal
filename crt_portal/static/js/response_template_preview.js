(function(root, dom) {
  function setContent(iframe, content) {
    iframe.contentWindow.document.open();
    iframe.contentWindow.document.write(content);
    iframe.contentWindow.document.close();
  }

  let populateController = new AbortController();
  function populatePreviewContent(form, previewContainer) {
    const formData = Object.fromEntries(new FormData(form));
    populateController.abort();
    populateController = new AbortController();
    window
      .fetch('/api/preview-response/', {
        method: 'POST',
        signal: populateController.signal,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': formData.csrfmiddlewaretoken
        },
        mode: 'same-origin',
        body: JSON.stringify(formData)
      })
      .then(response => response.text().then(rendered => setContent(previewContainer, rendered)))
      .catch(error => {
        console.error(error);
      });
  }

  function listenForChanges(form, previewContainer) {
    form.addEventListener('change', function() {
      populatePreviewContent(form, previewContainer);
    });
  }

  function setupPreview() {
    const form = document.forms.responsetemplate_form;

    const targets = dom.querySelectorAll('.response-template-preview');
    targets.forEach(target => populatePreviewContent(form, target));
    targets.forEach(target => listenForChanges(form, target));
  }

  root.addEventListener('load', setupPreview);
})(window, document);
