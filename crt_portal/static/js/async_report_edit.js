(function(root, dom) {
  const ALERT_TEMPLATE = `
    <div class="usa-alert async-response-message usa-alert--ALERT_TYPE usa-alert">
      <div class="usa-alert__body">
        <img src="/static/img/intake-icons/ic_close.svg" class="icon close-icon" aria-role="button" alt="close">
        <p class="usa-alert__text">
          ALERT_MESSAGE
        </p>
      </div>
    </div>
  `;

  function showAlert(container, message) {
    const alert = dom.createElement('div');
    alert.innerHTML = ALERT_TEMPLATE.replace('ALERT_TYPE', message.type).replace(
      'ALERT_MESSAGE',
      message.message
    );
    alert.querySelector('.close-icon').addEventListener('click', () => {
      alert.remove();
    });
    container.appendChild(alert);
    container.hidden = false;
  }

  function renderMessage(message) {
    if (!message.field || message.field == '__all__') {
      const container = dom.getElementById('page-errors');
      showAlert(container, message);
      return;
    }

    const field = dom.querySelector(`[name="${message.field}"]`).closest('div');
    if (!field) {
      console.error(`Field ${message.field} not found`);
      return;
    }
    showAlert(field, message);
  }

  function showResponseMessages(json) {
    dom.querySelectorAll('.async-response-message').forEach(alert => alert.remove());
    if (json.messages) {
      json.messages.forEach(message => {
        renderMessage(message);
      });
    }
  }

  function displayOk(response, json, form) {
    if (json.new_url) {
      root.history.replaceState({}, '', json.new_url);
      maybeDisablePublicIdField(form);
    }
    json.changed_data.forEach(key => {
      const value = json.form[key];
      const element = form.querySelector(`[name="${key}"]`);
      if (!element) {
        console.error(`Element with name ${key} not found`);
        return;
      }
      element.value = value;
    });
  }

  function save(saveButton) {
    const form = document.getElementById(saveButton.dataset.saves);
    const formData = new FormData(form);
    const url = form.action;
    const method = form.method;
    const token = formData.get('csrfmiddlewaretoken');
    formData.delete('csrfmiddlewaretoken');

    console.log(url, method, Object.fromEntries(formData));
    window
      .fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token
        },
        mode: 'same-origin',
        body: JSON.stringify(Object.fromEntries(formData))
      })
      .then(response => {
        response.json().then(json => {
          showResponseMessages(json);
          if (response.ok) {
            displayOk(response, json, form);
          }
        });
      })
      .catch(error => {
        showResponseMessages(json);
      });
  }

  function maybeDisablePublicIdField(form) {
    const publicIdField = form.querySelector('[name="public_id"]');
    const publicId = publicIdField.value;
    if (publicId && publicId.length > 0) {
      publicIdField.setAttribute('readonly', 'readonly');
    } else {
      publicIdField.removeAttribute('readonly');
    }
  }

  root.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form').forEach(form => {
      maybeDisablePublicIdField(form);
    });

    document.querySelectorAll('button[data-saves]').forEach(saveButton => {
      saveButton.addEventListener('click', () => save(saveButton));
    });
  });
})(window, document);
