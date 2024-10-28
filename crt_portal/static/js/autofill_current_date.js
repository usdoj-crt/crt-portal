(function(root, dom) {
  root.CRT = root.CRT || {};

  function autofillTodaysDate(inputEls) {
    const today = new Date();
    const day = today.getDate(),
      month = today.getMonth() + 1,
      year = today.getFullYear();
    [...inputEls].forEach(inputEl => {
      const inputName = inputEl.getAttribute('name');
      if (inputName.includes('month')) {
        inputEl.value = month;
      } else if (inputName.includes('day')) {
        inputEl.value = day;
      } else if (inputName.includes('year')) {
        inputEl.value = year;
      }
    });
  }

  document.querySelectorAll('.autofill_today_btn').forEach(autofillButton => {
    autofillButton.addEventListener('click', event => {
      const inputs = event.target.parentElement.getElementsByTagName('input');
      autofillTodaysDate(inputs);
    });
  });

  document.querySelectorAll('.autotoday').forEach(input => {
    autofillTodaysDate([input]);
  });

  return root;
})(window, document);
