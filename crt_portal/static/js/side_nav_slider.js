(function(root, dom) {
    function toggleMenu () {
        const sideNav = document.querySelector('.side-nav');
        sideNav.classList.toggle('open');
    }
    function setUpSideNav () {
        const mainWrapper = document.querySelector('.main-wrapper');
        mainWrapper.classList.add('display-flex');
        const menuSlider = mainWrapper.querySelector('.menu-slider');
        menuSlider.addEventListener('click', toggleMenu)
    }

  window.addEventListener('DOMContentLoaded', setUpSideNav);
})(window, document);