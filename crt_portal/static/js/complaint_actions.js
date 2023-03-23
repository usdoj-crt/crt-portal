(function(root, dom) {
  function update_record_count(index, parent_table) {
    var action_notification_els = dom.getElementsByClassName('selection-action-notification');
    const action_notification_el = action_notification_els[index];
    var count_el = action_notification_el.getElementsByClassName('selection-action-count')[0];
    var count = parent_table.querySelectorAll('td input.usa-checkbox__input:checked').length;
    if (count === 0) {
      action_notification_el.setAttribute('hidden', 'hidden');
    } else {
      var records_plural = count === 1 ? ' record' : ' records';
      count_el.innerText = count + records_plural;
      action_notification_el.removeAttribute('hidden');
    }
  }

  function addCheckAllListener(select_all_checkbox, all_checkboxes) {
    select_all_checkbox.addEventListener('click', event => {
      var checked = event.target.checked;
      for (var i = 0; i < all_checkboxes.length; i++) {
        var checkbox = all_checkboxes[i];
        if (checkbox.checked !== checked) {
          checkbox.click(); // trigger onclick function
        }
      }
    });
  }

  function addCheckboxListener(checkbox, index, parent_table) {
    checkbox.addEventListener('click', event => {
      var target = event.target;
      var parent = target.parentNode.parentNode.parentNode;
      if (target.checked) {
        parent.classList.add('selected');
      } else {
        parent.classList.remove('selected');
        if (select_all_checkboxes[j].checked) {
          select_all_checkboxes[j].checked = false;
        }
      }
      update_record_count(index, parent_table);
    });
  }

  var select_all_checkboxes = dom.getElementsByClassName('checkbox-input-all');
  for (let j = 0; j < select_all_checkboxes.length; j++) {
    var parent_table = select_all_checkboxes[j].closest('.usa-table.crt-table');
    var all_checkboxes = parent_table.querySelectorAll('td input.usa-checkbox__input');
    for (var i = 0; i < all_checkboxes.length; i++) {
      var checkbox = all_checkboxes[i];
      addCheckboxListener(checkbox, j, parent_table);
    }
    addCheckAllListener(select_all_checkboxes[j], all_checkboxes);
  }
})(window, document);
