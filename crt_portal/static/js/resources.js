(function(root, dom) {
  function copyContents(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
  }

  function addCopyButtonListener(copyButton, parentTable, actionNotificationEl, countEl) {
    const checkBoxes = parentTable.querySelectorAll('td input.usa-checkbox__input:checked');
    copyButton.addEventListener('click', e => {
      e.preventDefault();
      const resources = [];
      checkBoxes.forEach(checkBox => {
        const row = checkBox.closest('.tr--hover');
        const resourceText = row.querySelector('.copy-text');
        resources.push(resourceText.textContent);
      });
      copyContents(resources.join(''));
      copyButton.hidden = true;
      countEl.innerText = 'Saved to clipboard!';
      setTimeout(() => {
        actionNotificationEl.hidden = true;
      }, 2000);
    });
  }

  function updateResourceCount(index, parentTable) {
    const actionNotificationEls = dom.getElementsByClassName('selection-action-notification');
    const actionNotificationEl = actionNotificationEls[index];
    const countEl = actionNotificationEl.getElementsByClassName('selection-action-count')[0];
    const copyButton = actionNotificationEl.getElementsByTagName('button')[0];
    const count = parentTable.querySelectorAll('td input.usa-checkbox__input:checked').length;
    if (count === 0) {
      actionNotificationEl.hidden = true;
    } else {
      const resourcesPlural = count === 1 ? ' resource ' : ' resources ';
      countEl.innerText = count + resourcesPlural + 'selected';
      copyButton.hidden = false;
      copyButton.innerText = 'Copy' + resourcesPlural;
      actionNotificationEl.hidden = false;
    }
    addCopyButtonListener(copyButton, parentTable, actionNotificationEl, countEl);
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

  function addCheckboxListener(checkbox, index, parentTable) {
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
      updateResourceCount(index, parentTable);
    });
  }

  function copyRow(e) {
    const row = e.target.closest('.tr--hover');
    const resourceText = row.querySelector('.copy-text').textContent;
    copyContents(resourceText);
    const copyText = row.getElementsByClassName('copied')[0];
    const copyIcon = row.getElementsByClassName('copy-resource')[0];
    copyText.style.display = 'block';
    copyIcon.style.display = 'none';
    setTimeout(() => {
      copyText.style.display = 'none';
      copyIcon.style.display = 'block';
    }, 2000);
  }

  const selectAllCheckboxes = dom.getElementsByClassName('checkbox-input-all');
  for (let index = 0; index < selectAllCheckboxes.length; index++) {
    const parentTable = selectAllCheckboxes[index].closest('.usa-table.crt-table');
    const allCheckboxes = parentTable.querySelectorAll('td input.usa-checkbox__input');
    allCheckboxes.forEach(checkbox => {
      addCheckboxListener(checkbox, index, parentTable);
    });
    addCheckAllListener(selectAllCheckboxes[index], allCheckboxes);
  }

  const copyButtons = document.querySelectorAll('.copy-resource');
  copyButtons.forEach(function(btn) {
    btn.onclick = function(event) {
      event.preventDefault();
      copyRow(event);
    };
  });
})(window, document);
