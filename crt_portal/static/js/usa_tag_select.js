(function(root, dom) {
  function updateComboOptions(select, checkboxes) {
    select.innerHTML = '';
    checkboxes.forEach(checkbox => {
      if (checkbox.checked) return;
      const option = document.createElement('option');
      option.value = checkbox.value;
      option.innerHTML = checkbox.dataset.label;
      select.appendChild(option);
    });
  }

  function listenForSelect(wrapper) {
    const select = wrapper.querySelector('.usa-combo-box.assign-tag select');
    const checkboxes = wrapper.querySelectorAll('.usa-selected-tags input[type="checkbox"]');
    const selectedTags = wrapper.querySelector('.usa-selected-tags');
    select.addEventListener('change', event => {
      if (!event.target.value) return;
      const tagId = event.target.value;
      select.value = '';
      selectedTags.querySelector(`input[value="${tagId}"]`).checked = true;
      updateComboOptions(select, checkboxes);
      setTimeout(() => {
        wrapper.querySelector('.usa-combo-box__clear-input').click();
      });
    });
  }

  function listenForDeselect(wrapper) {
    const select = wrapper.querySelector('.usa-combo-box.assign-tag select');
    const checkboxes = wrapper.querySelectorAll('.usa-selected-tags input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
      const label = checkbox.nextElementSibling;
      label.addEventListener('keypress', function(event) {
        if (!['Enter', ' '].includes(event.key)) return;
        checkbox.click();
      });
      checkbox.addEventListener('change', event => {
        if (!wrapper.closest('.details-form-edit')) {
          // Edit mode is off.
          checkbox.checked = true;
          event.preventDefault();
          event.stopPropagation();
          return false;
        }
        updateComboOptions(select, checkboxes);
      });
    });
  }

  function attachListeners(wrapper) {
    listenForSelect(wrapper);
    listenForDeselect(wrapper);
  }

  root.addEventListener('load', () => {
    const wrappers = dom.querySelectorAll('.usa-tags-container');
    wrappers.forEach(wrapper => {
      const select = wrapper.querySelector('.usa-combo-box.assign-tag select');
      const checkboxes = wrapper.querySelectorAll('.usa-selected-tags input[type="checkbox"]');
      updateComboOptions(select, checkboxes);
      attachListeners(wrapper);
    });
  });
})(window, document);
