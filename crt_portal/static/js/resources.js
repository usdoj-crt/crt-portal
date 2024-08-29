(function(root, dom) {
  const copyButtons = document.querySelectorAll('.copy-resource');
  copyButtons.forEach(function(btn) {
    btn.onclick = function(event) {
      event.preventDefault();
      copyText(event);
    };
  });
  function copyText(e) {
    const row = e.target.closest('.tr--hover');
    const resourceText = row.querySelector('.copy-text');
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(resourceText);
    selection.removeAllRanges();
    selection.addRange(range);
    // using deprecated execCommand function to maintain formatting lost when using navigate
    document.execCommand('copy');
    window.getSelection().removeAllRanges();
    const copyText = row.getElementsByClassName('copied')[0];
    const copyIcon = row.getElementsByClassName('copy-resource')[0];
    copyText.style.display = 'block';
    copyIcon.style.display = 'none';
    setTimeout(() => {
      copyText.style.display = 'none';
      copyIcon.style.display = 'block';
    }, 2000);
  }
})(window, document);
