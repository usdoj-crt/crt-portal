(function(root) {
  const host = document.location.host;

  //If referrer is same domain, do not include
  const referrer = document.referrer.includes(host) ? '' : document.referrer;
  let localStorageReferrer = localStorage.getItem('referrer');

  if (referrer && !localStorageReferrer) {
    localStorage.setItem('referrer', referrer);
    localStorageReferrer = referrer;
  }
  console.log('localStorageReferrer', localStorageReferrer);
  if (localStorageReferrer) {
    let referrerEl = document.getElementById('id_0-referrer');
    if (referrerEl) {
      referrerEl.value = localStorageReferrer;
    }
  }
})(window);
