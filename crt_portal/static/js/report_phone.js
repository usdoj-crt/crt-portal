(function() {
  function setupInput(input) {
    // The input doesn't typically include the country code,
    // so we need to add a hidden input to store the full number
    const inputWithCountry = input.cloneNode(true);
    inputWithCountry.setAttribute('id', '');
    inputWithCountry.classList.add('display-none');
    input.setAttribute('name', '');
    input.insertAdjacentElement('afterend', inputWithCountry);

    const telInputApi = window.intlTelInput(input, {
      utilsScript: '/static/vendor/utils.js',
      initialCountry: 'us',
      showSelectedDialCode: true,
      nationalMode: true
    });

    function handleChange() {
      showValidity(input, telInputApi);
      inputWithCountry.value = telInputApi.getNumber();
    }
    input.addEventListener('change', handleChange);
    input.addEventListener('keyup', handleChange);
  }

  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.phone-input').forEach(setupInput);
  });

  function isValid(input, telInputApi) {
    if (!input.value) return null;
    const country = telInputApi.getSelectedCountryData() || {};
    if (country.iso2 === 'us' && telInputApi.getNumber().length !== 12) return false;
    if (!telInputApi.isValidNumber()) return false;

    return true;
  }

  function showValidity(input, telInputApi) {
    const validity = isValid(input, telInputApi);
    const invalidMessage = input.getAttribute('title' || 'Invalid phone number');
    input.setCustomValidity(validity ? '' : invalidMessage);
    input.reportValidity();

    if (validity === null) {
      input.classList.toggle('phone-input--error', false);
      input.classList.toggle('phone-input--valid', false);
    } else {
      input.classList.toggle('phone-input--error', !validity);
      input.classList.toggle('phone-input--valid', validity);
    }
  }
})();
