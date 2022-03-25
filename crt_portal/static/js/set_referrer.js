(function(root) {
  referrer = document.referrer;
  host = document.location.host;
  if (referrer.indexOf(host) > -1) {
    return;
  }

  if (localStorage.getItem('referrer') == null && referrer != '') {
    localStorage.setItem('referrer', referrer);
  }

  if (localStorage.getItem('referrer') != null && localStorage.getItem('referrer') != '') {
    referrerField = document.getElementById("id_0-referrer");
    if (referrerField) {
      referrerField.value = referrer;
    }
  }
})(window);