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

  function setupButtons() {
    const targets = dom.querySelectorAll('.admin-copy').forEach(createCopyButton);
  }

  root.addEventListener('load', setupButtons);
})(window, document);
