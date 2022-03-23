(function(root) {
  let header = document.getElementsByClassName('crt-landing--header')[0];
  let toc = document.getElementById('toc');
  let topNavLink = document.getElementById('sticky-nav-top');
  topNavLink.className = 'usa-sidenav__item usa-current';

  if (toc) {
    const spy = new Gumshoe('#toc a', {});

    toc.addEventListener('gumshoeActivate', function(event) {
      let link = event.detail.link;
      link.className = 'usa-current';
      topNavLink.className = 'usa-sidenav__item';
    });

    toc.addEventListener('gumshoeDeactivate', function(event) {
      let link = event.detail.link;
      link.className = null;
      topNavLink.className = 'usa-sidenav__item usa-current';
    });
  }
})(window);
