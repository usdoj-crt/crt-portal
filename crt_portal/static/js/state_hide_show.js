(function(root, dom) {
  function showState(state) {
    if (!state) state = 'default';

    dom.querySelectorAll('.state-hide-show').forEach(element => {
      element.hidden = true;
    });

    const toShow = dom.querySelectorAll(`.state-hide-show[data-state="${state}"]`);
    toShow.forEach(element => {
      element.hidden = false;
    });

    if (state !== 'default' && !toShow().length) {
      showState('default');
    }
  }

  dom.querySelectorAll('.state-hide-show-selector').forEach(element => {
    element.addEventListener('change', () => {
      showState(element.value);
    });
  });

  root.addEventListener('DOMContentLoaded', () => {
    showState('default');
  });
})(window, document);
