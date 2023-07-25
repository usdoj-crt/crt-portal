(function(root) {
  function getModal() {
    return document.getElementById('intake_referral_modal');
  }

  function getOpenModalButton() {
    return document.getElementById('refer_complaint');
  }

  function getCloseModalButton() {
    return getModal().querySelector('button.cancel');
  }

  function showModal(event) {
    event.preventDefault();
    const modal = getModal();
    if (modal.getAttribute('hidden') !== null) {
      root.CRT.openModal(modal);
    } else {
      root.CRT.closeModal(modal);
    }
  }

  function setLanguageCookie(lang) {
    document.cookie = `form-letter-language=${lang}`;
  }

  function getLanguageCookie() {
    const name = 'form-letter-language=';
    const cookieJar = document.cookie.split(';');
    return cookieJar.find(cookie => cookie.startsWith(name))?.replace(name, '');
  }

  function getLanguageSelect() {
    return getModal().querySelector('.language-select');
  }

  function applyTemplateLanguageFilter() {
    const modal = getModal();
    const languageSelect = getLanguageSelect();
    const selectedLanguage = languageSelect.value;

    const toHide = modal.querySelectorAll(
      `.intake-select > option.usa-select:not([data-language=${selectedLanguage}])`
    );
    const toShow = modal.querySelectorAll(
      `.intake-select > option.usa-select[data-language=${selectedLanguage}]`
    );

    toHide.forEach(el => el.setAttribute('hidden', 'true'));
    toShow.forEach(el => el.removeAttribute('hidden'));

    modal.querySelector('.response-template-referral').selectedIndex = 0;
  }

  function initLanguage() {
    getLanguageSelect().onchange = function(event) {
      event.preventDefault();
      applyTemplateLanguageFilter();
      setLanguageCookie(languageSelect.value);
    };

    if (getLanguageCookie()) {
      languageSelect.value = getLanguageCookie();
    }
    applyTemplateLanguageFilter();
  }

  function initModal() {
    getOpenModalButton().addEventListener('click', showModal);
    root.CRT.cancelModal(getModal(), getCloseModalButton());
    initLanguage();
  }

  initModal();
})(window);
