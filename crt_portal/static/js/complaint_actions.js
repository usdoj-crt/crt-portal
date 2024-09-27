(function(root, dom) {
  function updateRecordCount(index, parentTable, selectAllCheckbox) {
    const actionNotificationEls = dom.getElementsByClassName('selection-action-notification');
    const actionNotificationEl = actionNotificationEls[index];
    const countEl = actionNotificationEl.getElementsByClassName('selection-action-count')[0];
    const count = parentTable.querySelectorAll('td input.usa-checkbox__input:checked').length;
    const totalReports = parentTable.querySelector('#total_reports');
    const selectionWarning = actionNotificationEl.querySelector('.selection-warning');
    if (count === 0) {
      actionNotificationEl.hidden = true;
    } else if (selectAllCheckbox.checked && totalReports) {
      const numReports =
        totalReports.getAttribute('value') < 500 ? totalReports.getAttribute('value') : 500;
      const recordsPlural = numReports === 1 ? ' record' : ' records';
      countEl.innerText = numReports + recordsPlural;
      selectionWarning.hidden = !(totalReports.getAttribute('value') > 500);
      actionNotificationEl.hidden = false;
    } else {
      const recordsPlural = count === 1 ? ' record' : ' records';
      countEl.innerText = count + recordsPlural;
      if (totalReports) {
        selectionWarning.hidden = true;
      }
      actionNotificationEl.hidden = false;
    }
  }

  function updateBatchRecordCount(index, parentTable, selectAllCheckbox, visibleReports) {
    const actionNotificationEls = dom.getElementsByClassName('selection-action-notification');
    const actionNotificationEl = actionNotificationEls[index];
    const countEl = actionNotificationEl.getElementsByClassName('selection-action-count')[0];
    const count = parentTable.querySelectorAll('td input.usa-checkbox__input:checked').length;
    const selectedAll = dom.querySelector('.selected-all');
    const selectedSome = dom.querySelector('.selected-some');
    if (count === 0) {
      actionNotificationEl.hidden = true;
    } else if (selectAllCheckbox.checked) {
      const selectedAllBtn = actionNotificationEl.querySelector('.selection-action-count-btn');
      selectedSome.hidden = true;
      selectedAll.hidden = false;
      const numReports = visibleReports.getAttribute('value');
      selectedAllBtn.innerText = numReports + ' records';
      actionNotificationEl.hidden = false;
    } else {
      selectedSome.hidden = false;
      selectedAll.hidden = true;
      const recordsPlural = count === 1 ? ' record' : ' records';
      countEl.innerText = count + recordsPlural;
      actionNotificationEl.hidden = false;
    }
  }

  function addCheckAllListener(selectAllCheckbox, allCheckboxes) {
    selectAllCheckbox.addEventListener('click', event => {
      const checked = event.target.checked;
      allCheckboxes.forEach(checkbox => {
        if (checkbox.checked !== checked) {
          checkbox.click();
        }
      });
    });
  }

  function addCheckboxListener(checkbox, index, parentTable, selectAllCheckbox) {
    const visibleReports = parentTable.querySelector('#visible_reports');
    checkbox.addEventListener('click', event => {
      const target = event.target;
      const parent = target.parentNode.parentNode.parentNode;
      if (target.checked) {
        parent.classList.add('selected');
      } else {
        parent.classList.remove('selected');
        if (selectAllCheckboxes[index].checked) {
          selectAllCheckboxes[index].checked = false;
        }
      }
      if (visibleReports) {
        updateBatchRecordCount(index, parentTable, selectAllCheckbox, visibleReports);
      } else {
        updateRecordCount(index, parentTable, selectAllCheckbox);
      }
    });
  }

  const selectAllCheckboxes = dom.getElementsByClassName('checkbox-input-all');
  for (let index = 0; index < selectAllCheckboxes.length; index++) {
    const parentTable = selectAllCheckboxes[index].closest('.usa-table.crt-table');
    const allCheckboxes = parentTable.querySelectorAll('td input.usa-checkbox__input');
    allCheckboxes.forEach(checkbox => {
      addCheckboxListener(checkbox, index, parentTable, selectAllCheckboxes[index]);
    });
    addCheckAllListener(selectAllCheckboxes[index], allCheckboxes);
  }
})(window, document);
