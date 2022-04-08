(function (root, dom) {
  root.CRT = root.CRT || {};

  function autofillTodaysDate(event) {
    var inputEL = event.target.parentElement.getElementsByTagName('input');
    var today = new Date();
    var day = today.getDate(),
      month = today.getMonth() + 1,
      year = today.getFullYear();
    for (i = 0; i < inputEL.length; i++) {
      if (inputEL[i].getAttribute('name').includes('month')) {
        inputEL[i].value = month;
      } else if (inputEL[i].getAttribute('name').includes('day')) {
        inputEL[i].value = day;
      } else if (inputEL[i].getAttribute('name').includes('year')) {
        inputEL[i].value = year;
      }
    }
  }

  var autofill_btns = document.getElementsByClassName('autofill_today_btn');
  for (i = 0; i < autofill_btns.length; i++) {
    autofill_btns[i].addEventListener('click', autofillTodaysDate);
  }

  return root;
})(window, document);
