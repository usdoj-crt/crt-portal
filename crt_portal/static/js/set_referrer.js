(function(root) {
  referrer = document.referrer;
  host = document.location.host
  if (referrer.indexOf(host) > -1) {
    return
  }

  if (localStorage.getItem('referrer') == null && referrer != '') {
    localStorage.setItem('referrer', referrer)
  }
})(window);
