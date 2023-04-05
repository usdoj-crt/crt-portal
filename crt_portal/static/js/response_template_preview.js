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

  function pasteMarkdown(event, input) {
    const turndown = new TurndownService();
    let pastedHtml = event.clipboardData.getData('text/html');
    // Turndown escapes underscores so maintain them in links by replacing them before processing
    const parser = new DOMParser();
    const htmlDoc = parser.parseFromString(pastedHtml, 'text/html');
    const aTags = Array.from(htmlDoc.getElementsByTagName('a'));
    aTags.forEach(aTag => {
      const newhref = aTag['href'].replaceAll('_', '(UNDERSCORE)');
      pastedHtml = pastedHtml.replaceAll(aTag['href'], newhref);
    });
    const markdown = turndown.turndown(pastedHtml);
    // Word sometimes includes comments in its HTML, so strip them:
    const sanitized = markdown.replace(/<!--(?!>)[\S\s]*?-->/g, '').replaceAll('(UNDERSCORE)', '_');
    input.value =
      input.value.substring(0, input.selectionStart) +
      sanitized +
      input.value.substring(input.selectionEnd);
  }

  function listenForChanges(form, previewContainer) {
    const bodyInput = document.getElementById('id_body');
    bodyInput.addEventListener('paste', function(event) {
      pasteMarkdown(event, bodyInput);
      event.preventDefault();
      form.dispatchEvent(new Event('change'));
    });

    form.addEventListener('change', function() {
      populatePreviewContent(form, previewContainer);
    });

    const printButton = document.getElementById('print_template_preview');
    printButton.addEventListener('click', function(event) {
      previewContainer.contentWindow.print();
      event.preventDefault();
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
