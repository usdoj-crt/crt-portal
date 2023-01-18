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

    target.parentElement.appendChild(copyButton);
  }

  function makeAbsolute(input) {
    if (!input.classList.contains('absolute-url')) return;
    input.value = `${window.location.origin}${input.value}`;
  }

  function setupButtons() {
    const targets = dom.querySelectorAll('.admin-copy');
    targets.forEach(makeAbsolute);
    targets.forEach(createCopyButton);
  }

  root.addEventListener('load', setupButtons);
})(window, document);
