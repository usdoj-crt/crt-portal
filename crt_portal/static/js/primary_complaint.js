(function(doc) {
  var SELECTED_CLASS = 'selected';
  var cards = Array.prototype.slice.call(doc.querySelectorAll('.crt-hover-card'));

  function addClass(target, className) {
    target.classList.add(className);
  }

  function removeClass(target, className) {
    target.classList.remove(className);
  }

  function handleRadioSelect(el) {
    cards.forEach(function(card) {
      removeClass(card, SELECTED_CLASS);
    });

    addClass(el, SELECTED_CLASS);
  }

  cards.forEach(function(el) {
    const eventTarget = el.querySelector('input[type="radio"]');

    if (eventTarget.checked) {
      handleRadioSelect(el);
    }

    eventTarget.addEventListener('change', function() {
      handleRadioSelect(el);
    });
  });
})(document);
