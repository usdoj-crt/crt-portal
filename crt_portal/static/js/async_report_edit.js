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

    if (!json.changed_data) {
      return;
    }

    json.changed_data.forEach(key => {
      const value = json.form[key];
      // If value is undefined, we don't want to reset the element on the form
      if (!value) {
        return;
      }

      const element = form.querySelector(`[name="${key}"]`);
      if (!element) {
        console.error(`On Display OK: Element with name ${key} not found`);
        return;
      }

      switch (element.type) {
        case 'checkbox':
          form.querySelectorAll(`[name="${key}"]`).forEach(box => (box.checked = false));
          if (Array.isArray(value)) {
            value.forEach(val => {
              form
                .querySelectorAll(`[name="${key}"][value="${val}"]`)
                .forEach(box => (box.checked = true));
            });
          }
          break;
        default:
          element.value = value;
      }
    });
  }

  function save(saveButton) {
    const form = document.getElementById(saveButton.dataset.saves);
    const formData = new FormData(form);
    const url = form.action;
    const method = form.method;
    const token = formData.get('csrfmiddlewaretoken');
    const eeocChargeNumberRegExp = /^[A-Z0-9]{3}\-[A-Z0-9]{4}\-[A-Z0-9]{5}$/;
    formData.delete('csrfmiddlewaretoken');

    const formattedData = {};
    for (const [key, value] of formData) {
      if (!value) {
        continue;
      }

      let v = value;

      if (key === "eeoc_charge_number") {
        v = value.toUpperCase();

        if (!eeocChargeNumberRegExp.test(v)) {
          showResponseMessages({
            messages: [{
              field: 'eeoc_charge_number',
              type: 'error',
              message: 'Must be in the format XXX-XXXX-XXXXX'
            }]
          });
          return;
        }
      }
      // We need to do Array.from because document.getElementsByName returns a NodeList, not an Array
      const elements = Array.from(document.getElementsByName(key));

      // We are assuming that checkbox elements will always be formatted
      // as a list of values (an Array). We get only the first matching element's type
      // because we are assuming that all elements with the same name should have the same type.
      if (!Array.isArray(elements) || !elements.length) {
        console.error(`On Save: Element with name ${key} not found`);
        return;
      }

      const firstElement = elements[0];
      switch (firstElement.type) {
        case 'checkbox':
          if (!Object.keys(formattedData).includes(key)) {
            formattedData[key] = [];
          }
          formattedData[key].push(v);
          break;
        default:
          formattedData[key] = v;
      }
    }

    console.log(url, method, formattedData);
    window
      .fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token
        },
        mode: 'same-origin',
        body: JSON.stringify(formattedData)
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
