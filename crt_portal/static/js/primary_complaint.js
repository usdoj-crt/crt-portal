// Helper functions to apply the correct `selected` styles to the primary complaint cards
// Necessary becuase CSS does not allow styling of parent elements based on the
// state of child nodes.
(function (doc) {
  var SELECTED_CLASS = 'selected';
  var cards = Array.prototype.slice.call(doc.querySelectorAll('.crt-hover-card'));

  function addClass(target, className) {
    target.classList.add(className);
  }

  function removeClass(target, className) {
    target.classList.remove(className);
  }

  function handleRadioSelect(el) {
    cards.forEach(function (card) {
      removeClass(card, SELECTED_CLASS);
    });

    addClass(el, SELECTED_CLASS);
  }

  cards.forEach(function (el) {
    const eventTarget = el.querySelector('input[type="radio"]');

    // Ensure the `selected` class is applied to an issue that
    // is already selected when the page loads
    if (eventTarget.checked) {
      handleRadioSelect(el);
    }

    eventTarget.addEventListener('change', function () {
      handleRadioSelect(el);
    });
  });
})(document);
