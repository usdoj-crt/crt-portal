(function() {
  function resetChanges(button) {
    const form = button.closest('form');
    form.reset();
    form.querySelectorAll('.usa-combo-box').forEach(combobox => {
      const rawInput = combobox.querySelector('select');
      const uswdsInput = combobox.querySelector('input');
      uswdsInput.value = rawInput.options[rawInput.selectedIndex].text;
    });
  }

  document.querySelectorAll('.discard').forEach(discardButton => {
    discardButton.addEventListener('click', () => {
      resetChanges(discardButton);
    });
  });
})();
