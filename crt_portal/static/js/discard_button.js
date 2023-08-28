(function() {
  function resetChanges(button) {
    const form = button.closest('form');
    form.reset();
    [...form.getElementsByClassName('usa-combo-box')].forEach(combobox => {
      const select = combobox.getElementsByTagName('select')[0];
      select.nextSibling.value = select.value;
    });
  }

  document.querySelectorAll('.discard').forEach(discardButton => {
    discardButton.addEventListener('click', () => {
      resetChanges(discardButton);
    });
  });
})();
