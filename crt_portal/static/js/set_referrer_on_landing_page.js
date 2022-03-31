(function(root) {
  const host = document.location.host;
  console.log('host', host);
  //If referrer is same domain, do not include
  const referrer = document.referrer.includes(host) ? '' : document.referrer;
  console.log('referrer', referrer);

  if (referrer) {
    localStorage.setItem('referrer', referrer);
  }
  console.log("localStorage.getItem('referrer')", localStorage.getItem('referrer'));
})(window);
