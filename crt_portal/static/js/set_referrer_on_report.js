(function(root) {
  referrer = document.referrer;
  host = document.location.host;
  if (referrer.indexOf(host) > -1) {
    referrer = '';
  }

  if (localStorage.getItem('referrer') == null && referrer != '') {
    localStorage.setItem('referrer', referrer);
  }

  referrerInStorage = localStorage.getItem('referrer')
  if (referrerInStorage) {
    referrerField = document.getElementById("id_0-referrer");
    if (referrerField) {
      referrerField.value = referrerInStorage
    }
  }
})(window);

