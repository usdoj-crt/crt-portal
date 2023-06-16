/**
 * Unlike USWDS's builtin validation, does not restrict input.
 *
 * This can be useful for fields where users may want to paste a large value,
 * then trim it down before submission.
 *
 * For the list of supported value names, see:
 *   https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation#using_built-in_form_validation
 *
 * To use them without conflicting with builtin validation, use a "data-soft-"
 * attribute. For example:
 *
 * <textarea data-soft-valid data-soft-maxlength="5"></textarea>
 *
 */
(function(root, dom) {
  function markValid(element) {
    element.classList.remove('usa-input--error');
    element.dataset.softValid = true;
    if (element.nextElementSibling.classList.contains('soft-valid-message')) {
      element.nextElementSibling.remove();
    }

    if (!element.form?.querySelector('[data-soft-valid="false"]')) {
      element.form.querySelector('[type="submit"]').disabled = false;
    }
  }

  function markInvalid(element, clone) {
    element.classList.add('usa-input--error');
    element.dataset.softValid = false;
    element.setCustomValidity(clone.validationMessage);
    if (element.nextElementSibling.classList.contains('soft-valid-message')) {
      element.nextElementSibling.remove();
    }

    const message = document.createElement('span');
    message.classList.add('usa-error-message', 'soft-valid-message');
    message.textContent = clone.validationMessage;
    element.parentNode.insertBefore(message, element.nextElementSibling);

    if (element.form?.querySelector('[data-soft-valid="false"]')) {
      element.form.querySelector('[type="submit"]').disabled = true;
    }
  }

  function validate(event) {
    const element = event.currentTarget;
    const attrs = Object.entries(element.dataset)
      .filter(([name, data]) => {
        return name.startsWith('soft');
      })
      .map(([name, data]) => {
        return [name.replace('soft', '').toLowerCase(), data];
      });

    if (!attrs.length) return;

    const clone = element.cloneNode(true);
    attrs.forEach(([attr, data]) => {
      clone.setAttribute(attr, data);
    });
    if (clone.checkValidity()) {
      markValid(element);
    } else {
      markInvalid(element, clone);
    }
    clone.remove();
  }

  function listenForValidity(target) {
    target.addEventListener('input', validate);
    target.addEventListener('change', validate);
  }

  function addListeners() {
    dom.querySelectorAll('[data-soft-valid]').forEach(listenForValidity);
  }

  root.addEventListener('load', addListeners);
})(window, document);
