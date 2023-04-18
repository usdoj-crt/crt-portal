(function(root, dom) {
  function pasteDjNumber(event, combobox) {
    const pasted = event.clipboardData.getData('text/plain').trim();
    let components = pasted.split('-');
    if (components.length > 3) {
      components = [components.slice(0, -2).join('-'), ...components.slice(-2)];
    }

    console.log(components);

    if (components.length === 1) {
      // Try to paste this normally, as a single field.
      return;
    }

    event.preventDefault();
    event.stopPropagation();

    [...Array(components.length).keys()].forEach(index => {
      control = combobox.querySelector(`input#id_dj_number_${index}`);
      control.value = components[index];
      if (control.classList.contains('usa-combo-box__input')) {
        const select = control.previousElementSibling;
        select.value = components[index];
        select.dispatchEvent(new Event('change'));
        // Trigger the validation on the fancy combobox:
        control.focus();
        control.blur();
      } else {
        control.dispatchEvent(new Event('input'));
      }
    });

    // Reset focus in case we did fancy combobox validation:
    event.currentTarget.focus();
  }

  function listenForPaste(combobox) {
    combobox.querySelectorAll('input').forEach(input => {
      input.addEventListener('paste', event => pasteDjNumber(event, combobox));
    });
  }

  function attachListeners() {
    dom.querySelectorAll('.crt-dj-number').forEach(listenForPaste);
  }

  root.addEventListener('load', attachListeners);
})(window, document);
