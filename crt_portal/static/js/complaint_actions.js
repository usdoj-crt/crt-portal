(function(root, dom) {
  var all_checkboxes = dom.querySelectorAll('td input.usa-checkbox__input');
  for (var i = 0; i < all_checkboxes.length; i++) {
    var checkbox = all_checkboxes[i];
    checkbox.onclick = function(event) {
      var target = event.target;
      var parent = target.parentNode.parentNode.parentNode;
      if (target.checked) {
        parent.classList.add('selected');
      } else {
        parent.classList.remove('selected');
      }
    };
  }

  var select_all_checkboxes = dom.getElementById('checkbox-all');
  select_all_checkboxes.onclick = function(event) {
    var checked = event.target.checked;
    for (var i = 0; i < all_checkboxes.length; i++) {
      var checkbox = all_checkboxes[i];
      if (checkbox.checked !== checked) {
        checkbox.click(); // trigger onclick function
      }
    }
  };
})(window, document);
