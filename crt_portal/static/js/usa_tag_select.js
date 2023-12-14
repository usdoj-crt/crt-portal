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

  function checkAndChange(checkbox, shouldBeChecked) {
    checkbox.checked = shouldBeChecked;
    checkbox.dispatchEvent(new Event('click'));
    checkbox.dispatchEvent(new Event('change'));
  }

  function listenForSelect(wrapper) {
    const select = wrapper.querySelector('.usa-combo-box.assign-tag select');
    const checkboxes = wrapper.querySelectorAll('.usa-selected-tags input[type="checkbox"]');
    const selectedTags = wrapper.querySelector('.usa-selected-tags');
    select.addEventListener('change', event => {
      if (!event.target.value) return;
      const tagId = event.target.value;
      select.value = '';
      checkAndChange(selectedTags.querySelector(`input[value="${tagId}"]`), true);
      updateComboOptions(select, checkboxes);
      setTimeout(() => {
        wrapper.querySelector('.usa-combo-box__clear-input').click();
      });
    });
  }

  function listenForDropdownOpen(wrapper) {
    const ul = wrapper.querySelector('.usa-combo-box ul.usa-combo-box__list');
    const observer = new MutationObserver(mutations => {
      mutations.forEach((mutation, observer) => {
        mutation.addedNodes.forEach(maybeComboBoxItem => {
          styleExpandedDropdown(maybeComboBoxItem);
        });
      });
    });
    observer.observe(ul, { childList: true });
  }

  function styleExpandedDropdown(comboBoxItem) {
    if (!comboBoxItem.classList.contains('usa-combo-box__list-option')) return;

    const tagId = comboBoxItem.dataset.value;
    const checkbox = comboBoxItem
      .closest('.usa-tags-container')
      .querySelector(`.usa-selected-tags input[value="${tagId}"]`);

    comboBoxItem.innerHTML = checkbox.dataset.label;
  }

  function listenForDeselect(wrapper) {
    const select = wrapper.querySelector('.usa-combo-box.assign-tag select');
    const checkboxes = wrapper.querySelectorAll('.usa-selected-tags input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
      const label = checkbox.nextElementSibling;
      label.addEventListener('keypress', function(event) {
        if (!['Enter', ' '].includes(event.key)) return;
        checkAndChange(checkbox, false);
      });
      checkbox.addEventListener('change', event => {
        if (wrapper.closest('.details-form-view')) {
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
    listenForDropdownOpen(wrapper);
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
