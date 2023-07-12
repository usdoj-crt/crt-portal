(function(root, dom) {
  const tagComments = function() {
    document.querySelectorAll('.activity-stream-item').forEach(item => {
      const kind = item.innerText.includes('Added comment:') ? 'comment' : 'system';
      item.classList.add(kind);
    });
  };

  const toggleComment = function() {
    document.querySelectorAll('.activity-stream-item.system').forEach(item => {
      item.hidden = this.checked;
    });
    sendGAClickEvent('activity stream toggle comment');
  };
  toggleCommentButton = document.querySelector('#id_activity_comment');
  toggleCommentButton.addEventListener('change', toggleComment);

  root.addEventListener('load', tagComments);
})(window, document);
