(function(root) {
  function getModal() {
    return document.getElementById('intake_referral_modal');
  }

  function getReportId() {
    return document.getElementById('template-report-id').value;
  }

  function getOpenModalButton() {
    return document.getElementById('refer_complaint');
  }

  function getCloseModalButton(modal) {
    return modal.querySelector('button.cancel');
  }

  function reset(modal) {
    modal.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
    modal.closest('form').reset();

    const letterHtmls = modal.querySelectorAll('.letter-html');
    letterHtmls.forEach(letterHtml => {
      letterHtml.innerHTML = '';
      letterHtml.hidden = true;
    });
    const letterPlaintexts = modal.querySelectorAll('.letter-plaintext');
    letterPlaintexts.forEach(letterPlaintext => {
      letterPlaintext.innerHTML = '';
      letterPlaintext.hidden = false;
    });
    const subject = modal.querySelector('.subject');
    if (subject) {
      subject.innerHTML = '[Select an agency]';
    }
  }

  function showModal(event, modal) {
    event.preventDefault();
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

  function getLanguageSelect(modal) {
    return modal.querySelector('.language-select');
  }

  function applyTemplateLanguageFilter(modal) {
    const languageSelect = getLanguageSelect(modal);
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

  function initLanguage(modal) {
    const languageSelect = getLanguageSelect(modal);
    languageSelect.onchange = function(event) {
      event.preventDefault();
      applyTemplateLanguageFilter(modal);
      setLanguageCookie(languageSelect.value);
    };

    if (getLanguageCookie()) {
      languageSelect.value = getLanguageCookie();
    }
    applyTemplateLanguageFilter(modal);
  }

  function initAgencySelect(modal) {
    const templateField = modal.querySelector('.template-field');
    templateField.addEventListener('change', event => {
      modal.querySelector('.agency-restated').innerText = event.target.selectedOptions[0].innerText;
      templateField.classList.remove('error');

      // TODO: Use the combined pdf preview API, instead.
      root.CRT.renderTemplatePreview(modal, {
        reportId: getReportId(),
        responseTemplate: event.target.value,
        htmlBox: modal.querySelector('.complainant-letter .letter-html'),
        plaintextBox: modal.querySelector('.complainant-letter .letter-plaintext'),
        afterRendered: data => {
          const subject = modal.querySelector('.subject');
          if (!subject) return;
          subject.innerHTML = data.subject || '[Select an agency]';
        }
      });

      // TODO: Use the combined pdf preview API, instead.
      root.CRT.renderTemplatePreview(modal, {
        reportId: getReportId(),
        responseTemplate: event.target.value,
        htmlBox: modal.querySelector('.agency-letter .letter-html'),
        plaintextBox: modal.querySelector('.agency-letter .letter-plaintext'),
        afterRendered: data => {
          displayAgencyDetails(modal, data);
        }
      });
    });
  }

  function displayAgencyDetails(modal, data) {
    const details = modal.querySelector('.agency-email-details');
    if (!details) return;
    const yesEmail = document.querySelector('.yes-agency-email');
    const noEmail = document.querySelector('.no-agency-email');
    if (!data.referral_contact.addressee_emails?.trim().length) {
      noEmail.hidden = false;
      yesEmail.hidden = true;
      return;
    }
    noEmail.hidden = true;
    yesEmail.hidden = false;
    yesEmail.innerHTML = '';

    const emails = data.referral_contact.addressee_emails.split(',').map(e => e.trim());

    const to = document.createElement('p');
    to.innerHTML = `<strong>Email: </strong>${emails[0]}`;
    yesEmail.appendChild(to);

    const cc = document.createElement('p');
    cc.innerHTML = `<strong>CC: </strong>${emails.slice(1).join(', ')}`;
    yesEmail.appendChild(cc);

    const subject = document.createElement('p');
    subject.innerHTML = `<strong>Subject: </strong>${data.subject}`;
    yesEmail.appendChild(subject);
  }

  function getComplaintLetterInvalidReasons(modal, { currentStepName, targetStepName }) {
    const reasons = [];

    const templateField = modal.querySelector('.template-field');
    if (!templateField.querySelector('select').value) {
      reasons.push({
        field: templateField,
        userFacingError: 'Agency is required'
      });
    }

    return reasons;
  }
  function getAgencyLetterInvalidReasons(modal, { currentStepName, targetStepName }) {
    return [];
  }
  function getReviewAndSendInvalidReasons(modal, { currentStepName, targetStepName }) {
    return [];
  }

  function isComplaintLetterComplete(modal, { invalidReasons, currentStepName, targetStepName }) {
    return true;
  }
  function isAgencyLetterComplete(modal, { invalidReasons, currentStepName, targetStepName }) {
    return true;
  }
  function isReviewAndSendComplete(modal, { invalidReasons, currentStepName, targetStepName }) {
    return true;
  }

  function showModalValidity(modal, { completedSteps, invalidReasons, currentStep, targetStep }) {
    modal.querySelectorAll('.error').forEach(el => el.classList.remove('error'));

    Object.entries(invalidReasons).forEach(([invalidStep, reasons]) => {
      reasons.forEach(({ field, userFacingError }) => {
        if (!field) return;
        field.classList.add('error');
        if (userFacingError) {
          field.querySelector('.error-message').innerText = userFacingError;
        }
      });
    });
  }

  function getCanLeaveStep(
    modal,
    { completedSteps, invalidReasons, currentStepName, targetStepName }
  ) {
    if (currentStepName == 'complaintLetter') {
      return invalidReasons['complaintLetter'].length === 0;
    }
    return true;
  }

  const stepNames = {
    1: 'complaintLetter',
    2: 'agencyLetter',
    3: 'reviewAndSend'
  };

  const isStepComplete = {
    complaintLetter: isComplaintLetterComplete,
    agencyLetter: isAgencyLetterComplete,
    reviewAndSend: isReviewAndSendComplete
  };

  const getStepInvalidReasons = {
    complaintLetter: getComplaintLetterInvalidReasons,
    agencyLetter: getAgencyLetterInvalidReasons,
    reviewAndSend: getReviewAndSendInvalidReasons
  };

  function validateModal(modal, { currentStep, targetStep }) {
    const currentStepName = stepNames[currentStep];
    const targetStepName = stepNames[targetStep];
    const invalidReasons = Object.fromEntries(
      Object.entries(getStepInvalidReasons).map(([step, getInvalidReasons]) => {
        const context = { currentStepName, targetStepName };
        return [step, getInvalidReasons(modal, context)];
      })
    );
    const completedSteps = Object.fromEntries(
      Object.entries(isStepComplete).map(([step, isComplete]) => {
        const context = { invalidReasons, currentStepName, targetStepName };
        return [step, isComplete(modal, context)];
      })
    );

    const context = { completedSteps, invalidReasons, currentStepName, targetStepName };
    showModalValidity(modal, context);

    const canLeaveStep = getCanLeaveStep(modal, context);
    return { canLeaveStep, ...context };
  }

  function initModal() {
    const modal = getModal();
    const openButton = getOpenModalButton();
    const cancelButton = getCloseModalButton(modal);
    if (!openButton || !modal) return;
    openButton.addEventListener('click', event => showModal(event, modal));
    cancelButton.addEventListener('click', () => {
      reset(modal);
      modal.querySelector('.progress .steps').dataset.currentStep = 1;
      root.CRT.renderSteps(modal, validateModal);
    });
    root.CRT.cancelModal(modal, cancelButton);
    initLanguage(modal);
    initAgencySelect(modal);
    root.CRT.renderSteps(modal, validateModal);
  }

  initModal();
})(window);
