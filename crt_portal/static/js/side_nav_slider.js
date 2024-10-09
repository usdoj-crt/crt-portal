(function(root, dom) {
  const mainWrapperEls = document.querySelectorAll('.main-wrapper');
  const mainWrapper = mainWrapperEls[mainWrapperEls.length - 1];

  function toggleMenu() {
    const sideNav = document.querySelector('.side-nav');
    sideNav.classList.toggle('open');
  }

  function toggleAddModal() {
    const isOpen = document.querySelector('.side-nav').classList.contains('open');
    if (isOpen) return;
    const addModal = document.querySelector('.add-modal');
    addModal.hidden = !addModal.hidden;
  }

  function setUpSideNav() {
    mainWrapper.classList.add('display-flex');
    const menuSlider = dom.querySelector('.menu-slider');
    menuSlider.addEventListener('click', toggleMenu);

    document.querySelectorAll('.add-record-target').forEach(addRecord => {
      addRecord.addEventListener('click', toggleAddModal);
    });

    // Some items on the page calculate their size based on the side-nav
    // This resize event gives them a chance to recalculate their size following
    // the display-flex:
    window.dispatchEvent(new Event('resize'));
  }

  window.addEventListener('DOMContentLoaded', setUpSideNav);
})(window, document);
