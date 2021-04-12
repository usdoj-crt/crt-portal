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

  var remove_buttons = document.querySelectorAll('.remove-attachment-button');
  remove_buttons.forEach(function(btn) {
    btn.onclick = function(event) {
      event.preventDefault();

      var attachment_id = this.getAttribute('data-attachment-id');
      var attachment_filename = this.getAttribute('data-attachment-filename');

      // modal elements
      var modal = document.getElementById('attachment-removal-confirmation--modal');
      var filename_el = document.getElementById('attachment-removal--filename');
      var no_button = document.getElementById('attachment-removal--no');
      var yes_button = document.getElementById('attachment-removal--yes');

      // add the to-be-removed filename to the modal
      filename_el.innerText = attachment_filename;

      // user clicks no on removal confirmation
      no_button.onclick = function(event) {
        event.preventDefault();
        // do nothing, just hide the modal
        root.CRT.closeModal(modal);
      };

      // user clicks yes on removal confirmation
      yes_button.onclick = function(event) {
        event.preventDefault();

        // get the form for removing this particular attachment
        var form_id = `complaint-view-remove-attachment-${attachment_id}`;
        var form = document.getElementById(form_id);

        // submit the removal form
        form.submit();
      };

      root.CRT.openModal(modal);
    };
  });
})(window, document);
