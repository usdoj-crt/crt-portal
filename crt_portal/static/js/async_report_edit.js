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
    // TODO: Remove this debug statement
    console.log("DisplayOk: Changed Data = ", json.changed_data);

    json.changed_data.forEach(key => {
      const value = json.form[key];
      const element = form.querySelector(`[name="${key}"]`);

      // TODO: Remove these two debug statements
      console.log("DisplayOk: element = ", element);
      console.log("DisplayOk: value = ", value);
      if (!element) {
        console.error(`Element with name ${key} not found`);
        return;
      }
      /* 
        This line is causing LOTS of problems.
        For instance, when we save protected_class,
        it sets the value of the the first checkbox (usually 'Age')
        This causes a huge problem because we can set 'Age' to potentially:
          - A comma separated value of all of the saved values
          - Undefined, if there were no saved values for protected_class
        This massively breaks subsequent saves.

        In my testing, this line seems 100% uneccessary. Reasons are:
          - When the form is saved, the values on the frontend don't get reset
            (so there is no need to set them here again)
          - If you were to refresh the page the values on the form would be cleared regardless
            with no way to retrieve them. Entering the form_id and pressing "save" doesn't retrieve
            the current data, it will attempt overwrite the current data with empty values
            (so there is still no reason or need to set element values here)
      */
      // element.value = value;
    });
  }

  function save(saveButton) {
    const form = document.getElementById(saveButton.dataset.saves);
    const formData = new FormData(form);
    const url = form.action;
    const method = form.method;
    const token = formData.get('csrfmiddlewaretoken');
    formData.delete('csrfmiddlewaretoken');

    /*
      Lots of debugging output here. There is an issue with MultiSelectFields and this saving logic.
      The issue is only the last value checked ever gets saved. This is because when we get the FormData object
      for any MultiSelectFields it will show like this:

      Lets say for example we use protected_class field. Lets say "Age" has a value of '1'
      Lets also say "Religion" has value of '2', and lets say "Pregnancy" has a value of '3'.
      (I don't know if these are the actual values, but its just an example)

      Now, lets assume Age and Religion are checked. formData will look like this:
      {
        ...
        'protected_class': "1",
        'protected_class': "2",
        ...
      }

      Based on how we are doing the save logic with Object.fromEntries(formData):
      Object.fromEntires loops through the dictionary keys and just assigns them. So:
      protected_class: 1 will get overwritten by protected_class: 2. This is bad for two reasons:
        1. The data that gets submitted is wrong, because it is missing values.
        2. The data will fail validation, because we are expecting an Array of values.

      I have added a sort of dirty fix below where I go through formData and pull out duplicate key: value pairs
      for protected_class. This Should be the only field that behaves this way, and only on the CRU form for now.

      TODO:
      - Break this logic out into a function so it is more readable and clean
      - Clean up console.log statements

    */
    console.log("async_report_edit: FormData protected_class = ", formData.getAll('protected_class'));

    let debugOutput = "";

    let formattedData = {};
    for (const [key, value] of formData) {
      debugOutput += `${key}: ${value}\n`;

      /* 
        This feels sloppy to me but as a quick and dirty fix, it seems functional.
        I would love to have a more robust solution that doesn't check hard coded field names.
        If we could maybe check by field type or something? I.E: We know MultiSelectFields need an Array as
        their value type. I am not sure if we can get the type of field here in a clean way or not.
        I am also not sure if there are other ways that may be better to go about it.
      */
      switch (key) {
        case 'protected_class':
          if (!(Array.isArray(formattedData[key]))) {
            formattedData[key] = [];
          }
          if (value) {
            // TODO: Remove this debug statement
            console.log("protected_class Value = ", value);
            const formattedValues = value.split(',');
            for(const formattedValue of formattedValues) {
              // TODO: Remove this debug statement
              console.log("formattedValue = ", formattedValue);
              if (!formattedData[key].includes(formattedValue)) {
                formattedData[key].push(formattedValue);
              }
            }
          }
          break;
        default:
          formattedData[key] = value
      }
    }
    // TODO: Remove these debug statements
    console.log("async_report_edit: debug output = ", debugOutput);
    console.log("async_report_edit: FormattedData = ", formattedData);

    /* NOTE: The console log here was here before. Don't delete this.
      However, this is WRONG, and will showcase the issue described above
      due to Object.fromEntries on formData.
    */
    console.log(url, method, Object.fromEntries(formData));
    window
      .fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token
        },
        mode: 'same-origin',
        //  Submit the 'corrected' payload instead:
        // body: JSON.stringify(Object.fromEntries(formData))
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
