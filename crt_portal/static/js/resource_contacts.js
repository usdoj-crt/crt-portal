(function(root) {
  const addContactEl = document.getElementById('add_contact');
  const contactContainer = document.querySelector('.contact-container');
  const responseWrapper = document.getElementsByClassName('response-wrapper')[0];
  const contactInput = document.querySelector('#id_contacts');

  const removeLinks = document.querySelectorAll('.remove-contact-button');
  removeLinks.forEach(removeLink => {
    removeLink.onclick = function(event) {
      event.preventDefault();
      removeContact(event.target.getAttribute('data-contact-id'));
    };
  });

  addContactEl.onclick = function(event) {
    event.preventDefault();
    addContact(event);
  };

  function createRow(data) {
    const contactsTable = document.getElementById('contactsTable');
    const tableHead = document.querySelector('thead');
    tableHead.hidden = false;
    const newRow = document.createElement('tr');
    newRow.id = data.id + 'row';
    newRow.innerHTML = `
              <td>
                  ${data.first_name ?? ''} ${data.last_name ?? ''}
              </td>
              <td>
                  ${data.title ?? ''}
              </td>
              <td>
                  ${data.phone ?? ''}
              </td>
              <td>
                  ${data.email ?? ''}
              </td>
              <td>
                  <button data-contact-id="${data.id}" data-contact-name="${
      data.first_name
    }" class="usa-button usa-button--outline remove-contact-button">
                  <img data-contact-id="${
                    data.id
                  }" src="/static/img/trash-2.svg" alt="remove contact" class="icon"></button>
              </td>
              `;
    contactsTable.appendChild(newRow);
    const removeLink = newRow.querySelector('button');
    removeLink.onclick = function(event) {
      event.preventDefault();
      removeContact(data.id);
    };
    if (!contactInput.value) {
      contactInput.value = data.id + ',';
    } else {
      contactInput.value += data.id + ',';
    }
  }

  function removeContact(contactId) {
    const csrf = Cookies.get('csrftoken');
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrf);
    formData.append('action', 'removed');
    formData.append('contact_id', contactId);
    window
      .fetch('/api/resource-contact-action/', {
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
        const row = document.getElementById(`${data.id}row`);
        if (row) {
          row.remove();
        }
        responseWrapper.innerHTML =
          data.type == 'error'
            ? `<div class="usa-alert__body"><em class="usa-alert__text">${data.response}</em></div>`
            : '';
        responseWrapper.hidden = data.type != 'error';
        const contactInputVal = contactInput.value;
        const regex = new RegExp(data.id + ',');
        const newVal = contactInputVal.replace(regex, '');
        contactInput.value = newVal;
      })
      .catch(error => {
        console.error(error);
      });
  }

  function addContact(e) {
    e.preventDefault();
    const csrf = Cookies.get('csrftoken');
    const formData = new FormData();
    const firstName = contactContainer.querySelector('#id_first_name');
    const lastName = contactContainer.querySelector('#id_last_name');
    const title = contactContainer.querySelector('#id_title');
    const email = contactContainer.querySelector('#id_contact_email');
    const phone = contactContainer.querySelector('#id_contact_phone');
    formData.append('first_name', firstName.value);
    formData.append('last_name', lastName.value);
    formData.append('title', title.value);
    formData.append('email', email.value);
    formData.append('phone', phone.value);
    formData.append('csrfmiddlewaretoken', csrf);
    formData.append('action', 'added');
    window
      .fetch('/api/resource-contact-action/', {
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
        responseWrapper.innerHTML =
          data.type == 'error'
            ? `<div class="usa-alert__body"><em class="usa-alert__text">${data.response}</em></div>`
            : '';
        responseWrapper.hidden = data.type != 'error';
        if (data.id) {
          firstName.value = '';
          lastName.value = '';
          title.value = '';
          email.value = '';
          phone.value = '';
          createRow(data);
        }
      })
      .catch(error => {
        console.error(error);
      });
  }
})(window);
