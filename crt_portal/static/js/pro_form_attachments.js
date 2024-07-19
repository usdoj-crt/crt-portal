(function(root) {
    const add_attachment_el = document.getElementById('add_attachment');
    const file_el = document.getElementById('file_input');

    add_attachment_el.onclick = function(event) {
      event.preventDefault();
      file_el.click();
    };

    file_el.onchange = function(event) {
      const modal = document.getElementById('attachment-uploading--modal');
      root.CRT.openModal(modal);
      getAttachmentResponse(event, 'add', modal)
    };

    const remove_buttons = document.querySelectorAll('.remove-attachment-button');
    remove_buttons.forEach(function(btn) {
      btn.onclick = function(event) {
        event.preventDefault();

        const attachment_id = this.getAttribute('data-attachment-id');
        const attachment_filename = this.getAttribute('data-attachment-filename');

        // modal elements
        const modal = document.getElementById('attachment-removal-confirmation--modal');
        const filename_el = document.getElementById('attachment-removal--filename');
        const no_button = document.getElementById('attachment-removal--no');
        const yes_button = document.getElementById('attachment-removal--yes');

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

          getAttachmentResponse(event, 'remove', modal)
        };

        root.CRT.openModal(modal);
      };
    });

    function downloadAttachment(e) {
        const attachment_id = e.target.getAttribute('data-attachment-id');
        window
        .fetch('/api/proform-attachment-action/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken')
            },
            mode: 'same-origin',
            body: JSON.stringify({ attachment_id })
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            console.log(data);
        })
        .catch(error => {
            console.error(error);
        });
    }

    function getAttachmentResponse(e, action, modal) {
        e.preventDefault();
        const file = e.target.files[0]
        const csrf = Cookies.get('csrftoken')
        let formData = new FormData()
        formData.append('file', file)
        formData.append('action', action)
        formData.append('csrfmiddlewaretoken', csrf);
        window
        .fetch('/api/proform-attachment-action/', {
            method: 'POST',
            headers: {
            'X-CSRFToken': csrf
            },
            mode: 'same-origin',
            body: formData
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            const attachmentTable = document.getElementById('attachmentTable');
            const newRow = document.createElement('tr');
            newRow.innerHTML =
                `
                <td><a href="#" data-attachment-id="${data.id}"> ${file.name}</a></td>
                <td>
                    <button data-attachment-id="${data.id}" data-attachment-filename="${file.name}" class="usa-button usa-button--outline remove-attachment-button"> <img src="{% static "img/trash-2.svg" %}" class="icon" alt="remove attachment"></button>
                </td>
                `
            attachmentTable.appendChild(newRow);
            const downloadLink = newRow.querySelector('a');
            downloadLink.onclick = function(event) {
                event.preventDefault();
                downloadAttachment(e);
            }
            console.log(data);
            root.CRT.closeModal(modal);
        })
        .catch(error => {
            root.CRT.closeModal(modal);
            console.error(error);
        });
    }
})(window);