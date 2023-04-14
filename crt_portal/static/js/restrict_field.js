(function(root, dom) {
  function restrictNumber(event) {
    if (event.currentTarget.value === '') return;

    const min = event.currentTarget.getAttribute('min');
    const max = event.currentTarget.getAttribute('max');
    const newValue = event.currentTarget.value;

    if (min !== null && newValue < Number(min)) {
      event.currentTarget.value = min;
      return;
    }
    if (max !== null && newValue > Number(max)) {
      event.currentTarget.value = Math.min(Number(newValue.substring(0, max.length)), Number(max));
      return;
    }
  }

  function listenForNumber(target) {
    target.addEventListener('input', restrictNumber);
  }

  function addRestrictions() {
    dom.querySelectorAll('.crt-restrict-number').forEach(listenForNumber);
  }

  root.addEventListener('load', addRestrictions);
})(window, document);
