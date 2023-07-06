(function(root, dom) {
  const tagComments = function() {
    document.querySelectorAll('.activity-stream-item').forEach(item => {
      const kind = item.innerText.includes('Added comment:') ? 'comment' : 'system';
      item.classList.add(kind);
    });
  };

  const toggleSystem = function() {
    document.querySelectorAll('.activity-stream-item.system').forEach(item => {
      item.hidden = !this.checked;
    });
  };
  toggleSystemButton = document.querySelector('#id_activity_system');
  toggleSystemButton.addEventListener('change', toggleSystem);

  root.addEventListener('load', tagComments);
})(window, document);
