(function(root, dom) {
  root.CRT = root.CRT || {};

  document.addEventListener('DOMContentLoaded', function() {
    // `marked` should be loaded in global context at this point.
    if (marked) {
      marked.setOptions({
        gfm: true,
        breaks: true
      });
    } else {
      console.error('marked.js parser not loaded');
    }
  });

  function addReferralAddress(referral_contact) {
    const addressee = document.getElementById('form-letterhead--addressee');
    const deptAddressee = document.getElementById('form-letterhead--dept-addressee');

    if (deptAddressee) {
      deptAddressee.remove();
    }

    if (!addressee) return;

    const addressee_text = referral_contact?.addressee_text;
    if (!addressee_text) return;

    const newDeptAddressee = document.createElement('p');
    newDeptAddressee.id = 'form-letterhead--dept-addressee';
    newDeptAddressee.innerText = addressee_text;

    addressee.parentNode.insertBefore(newDeptAddressee, addressee);
  }

  function renderOptionals(container, optionals, rerender) {
    container.innerHTML = '';
    let checkboxId = 0;
    let currentRerender = null;
    Object.entries(optionals).map(([group, options]) => {
      const fieldset = document.createElement('fieldset');
      fieldset.classList.add('usa-fieldset');
      const legend = document.createElement('legend');
      legend.classList.add('usa-legend');
      legend.innerText = group;
      fieldset.appendChild(legend);

      function rerenderWithOptionals() {
        const userSelections = container.querySelectorAll('input[type="checkbox"]:checked');
        const selectedOptions = Array.from(userSelections)
          .map(input => [input.name, input.value])
          .reduce((acc, [name, value]) => {
            if (!acc[name]) acc[name] = [];
            acc[name].push(value);
            return acc;
          }, {});
        const serializedOptions = encodeURIComponent(JSON.stringify(selectedOptions));
        return rerender(serializedOptions);
      }

      const checkboxes = options.map(option => {
        const field = document.createElement('div');
        const label = document.createElement('label');
        const input = document.createElement('input');
        field.classList.add('usa-checkbox');
        input.classList.add('usa-checkbox__input');
        input.type = 'checkbox';
        input.name = group;
        input.value = option.name;
        input.addEventListener('change', () => {
          if (!currentRerender) {
            currentRerender = rerenderWithOptionals();
          } else {
            currentRerender = currentRerender.then(() => rerenderWithOptionals());
          }
        });
        input.id = `contact-optionals-${checkboxId++}`;
        label.htmlFor = input.id;
        label.classList.add('usa-checkbox__label');
        field.appendChild(input);
        field.appendChild(label);
        label.appendChild(document.createTextNode(option.name));
        return field;
      });
      checkboxes.forEach(checkbox => fieldset.appendChild(checkbox));
      container.appendChild(fieldset);
    });
    container.hidden = Object.keys(optionals).length === 0;
  }

  let currentResponseTemplate = null;

  root.CRT.renderTemplatePreview = function(
    modal,
    {
      reportId,
      responseTemplate,
      htmlBox,
      plaintextBox,
      optionals,
      afterRendered,
      selectedOptionals
    }
  ) {
    const params = new URLSearchParams();
    params.append('report_id', reportId);
    if (selectedOptionals) {
      params.append('optionals', selectedOptionals);
    }
    return window
      .fetch(`/api/responses/${responseTemplate}/?${params.toString()}`)
      .then(response => response.json())
      .then(data => {
        if (data.is_html) {
          plaintextBox.hidden = true;
          htmlBox.hidden = false;
          htmlBox.innerHTML = data.body ?? '';
        } else {
          htmlBox.hidden = true;
          plaintextBox.hidden = false;
          plaintextBox.innerHTML = data.body.replaceAll('<br>', '\n') ?? '';
        }
        if (responseTemplate !== currentResponseTemplate) {
          function rerender(chosenOptionals) {
            return root.CRT.renderTemplatePreview(modal, {
              reportId,
              responseTemplate,
              htmlBox,
              plaintextBox,
              optionals,
              afterRendered,
              selectedOptionals: chosenOptionals
            });
          }
          renderOptionals(optionals, data.optionals ?? {}, rerender);
          currentResponseTemplate = responseTemplate;
        }
        addReferralAddress(data.referral_contact);
        if (afterRendered) afterRendered(data);
      });
  };

  root.CRT.handleReferral = async function(action, { reportId, responseTemplate, recipient }) {
    const response = await window.fetch('/api/response-action/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken')
      },
      mode: 'same-origin',
      body: JSON.stringify({
        action,
        report_id: reportId,
        template_id: responseTemplate,
        recipient
      })
    });
    const data = await response.json();
    return { data, status: response.status };
  };
})(window, document);
