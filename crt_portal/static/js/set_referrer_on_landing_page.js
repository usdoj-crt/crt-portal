(function(root) {
  referrer = document.referrer;
  host = document.location.host;

  if (referrer) {
    localStorage.setItem('referrer', referrer);
  }
})(window);
