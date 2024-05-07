(function(root, dom) {
  const mainWrapperEls = document.querySelectorAll('.main-wrapper');
  const mainWrapper = mainWrapperEls[mainWrapperEls.length - 1];
  function toggleMenu() {
    const sideNav = document.querySelector('.side-nav');
    sideNav.classList.toggle('open');
    mainWrapper.classList.toggle('side-nav-open');
  }
  function setUpSideNav() {
    mainWrapper.classList.add('display-flex');
    const menuSlider = mainWrapper.querySelector('.menu-slider');
    menuSlider.addEventListener('click', toggleMenu);
  }

  window.addEventListener('DOMContentLoaded', setUpSideNav);
})(window, document);