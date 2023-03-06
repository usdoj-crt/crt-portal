(function(root, dom) {
  const COPY = 'Copy to Clipboard';

  function markAsCopied(button) {
    button.innerText = 'Copied!';
    button.setAttribute('disabled', 'disabled');
    setTimeout(() => {
      button.innerText = COPY;
      button.removeAttribute('disabled');
    }, 3000);
  }

  function createCopyButton(target) {
    const copyButton = document.createElement('button');
    copyButton.className = 'admin-copy-button button';
    const buttonContent = document.createTextNode(COPY);
    copyButton.appendChild(buttonContent);

    copyButton.onclick = () => {
      navigator.clipboard.writeText(target.value);
      markAsCopied(copyButton);
    };

    target.parentElement.classList.add('admin-copy-button-parent');
    target.parentElement.appendChild(copyButton);
  }

  function makeAbsolute(input) {
    if (!input.classList.contains('absolute-url')) return;
    const origin = getOrigin();
    input.value = `${origin}${input.value}`;
  }

  function getOrigin() {
    const origin = window.location.origin;
    if (origin.includes('crt-portal-django-prod.app.cloud.gov')) {
      return 'https://civilrights.justice.gov';
    }

    return origin;
  }

  function setupButtons() {
    const targets = dom.querySelectorAll('.admin-copy');
    targets.forEach(makeAbsolute);
    targets.forEach(createCopyButton);
  }

  root.addEventListener('load', setupButtons);
})(window, document);
