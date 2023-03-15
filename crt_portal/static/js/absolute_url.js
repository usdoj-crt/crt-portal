(function(root, dom) {
  function makeAbsolute(input) {
    const origin = getOrigin();
    input.value = `${origin}${input.value}`;
  }

  function getOrigin() {
    const origin = window.location.origin;
    if (origin.includes('crt-portal-django-prod.app.cloud.gov')) {
      return 'https://civilrights.justice.gov';
    }

    return origin;
  }

  function setup() {
    dom.querySelectorAll('.absolute-url').forEach(makeAbsolute);
  }

  root.addEventListener('load', setup);
})(window, document);
