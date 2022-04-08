(function (root, dom) {
  function update_record_count() {
    var action_notification_el = dom.querySelector('.selection-action-notification');
    var count_el = dom.getElementById('selection-action-count');
    var count = dom.querySelectorAll('td input.usa-checkbox__input:checked').length;
    if (count === 0) {
      action_notification_el.setAttribute('hidden', 'hidden');
    } else {
      var records_plural = count === 1 ? ' record' : ' records';
      count_el.innerText = count + records_plural;
      action_notification_el.removeAttribute('hidden');
    }
  }

  var select_all_checkboxes = dom.getElementById('checkbox-all');
  var all_checkboxes = dom.querySelectorAll('td input.usa-checkbox__input');
  for (var i = 0; i < all_checkboxes.length; i++) {
    var checkbox = all_checkboxes[i];
    checkbox.onclick = function (event) {
      var target = event.target;
      var parent = target.parentNode.parentNode.parentNode;
      if (target.checked) {
        parent.classList.add('selected');
      } else {
        parent.classList.remove('selected');
        if (select_all_checkboxes.checked) {
          select_all_checkboxes.checked = false;
        }
      }
      update_record_count();
    };
  }

  select_all_checkboxes.onclick = function (event) {
    var checked = event.target.checked;
    for (var i = 0; i < all_checkboxes.length; i++) {
      var checkbox = all_checkboxes[i];
      if (checkbox.checked !== checked) {
        checkbox.click(); // trigger onclick function
      }
    }
  };
})(window, document);
