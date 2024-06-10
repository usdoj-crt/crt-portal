(function(root, dom) {
  const mainWrapperEls = document.querySelectorAll('.main-wrapper');
  const mainWrapper = mainWrapperEls[mainWrapperEls.length - 1];
  function toggleMenu() {
    const sideNav = document.querySelector('.side-nav');
    sideNav.classList.toggle('open');
  }
  function setUpSideNav() {
    mainWrapper.classList.add('display-flex');
    const menuSlider = mainWrapper.querySelector('.menu-slider');
    menuSlider.addEventListener('click', toggleMenu);

    // Some items on the page calculate their size based on the side-nav
    // This resize event gives them a chance to recalculate their size following
    // the display-flex:
    window.dispatchEvent(new Event('resize'));
  }

  window.addEventListener('DOMContentLoaded', setUpSideNav);
})(window, document);
