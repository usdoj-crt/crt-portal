(function(root, dom) {
  var add_attachment_el = document.getElementById('add_attachment');
  var file_el = document.getElementById('file_input');

  add_attachment_el.onclick = function(event) {
    event.preventDefault();
    file_el.click();
  };

  file_el.onchange = function(event) {
    var form = document.getElementById('complaint-view-attachments');
    form.submit();

    var modal = document.getElementById('attachment-uploading--modal');
    root.CRT.openModal(modal);
  };
})(window, document);
