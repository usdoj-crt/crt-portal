(function(root) {
  referrer = document.referrer;
  host = document.location.host;

  if (localStorage.getItem('referrer') == null && referrer != '') {
    localStorage.setItem('referrer', referrer);
  }
})(window);