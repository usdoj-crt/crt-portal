(function(root) {
  function getModal() {
    return document.getElementById('intake_referral_modal');
  }

  function getReportId() {
    return document.getElementById('template-report-id').value;
  }

  function getPublicId() {
    return document.querySelector('.details-id h2').innerText.replaceAll('ID: ', '');
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
    });
    const subject = modal.querySelector('.subject');
    if (subject) {
      subject.innerHTML = '[Select an agency]';
    }

    applyTemplateLanguageFilter(modal);
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

      root.CRT.handleReferral('preview', {
        reportId: getReportId(),
        responseTemplate: event.target.value
      }).then(({ data }) => {
        displayComplainantDetails(modal, data?.complainant);
        displayAgencyDetails(modal, data?.agency);
      });
    });
  }

  function displayComplainantDetails(modal, data) {
    const section = modal.querySelector('.complainant-letter');
    const subjects = modal.querySelectorAll('.complainant.subject');
    subjects.forEach(s => (s.innerText = data?.letter?.subject || '[Select an agency]'));
    const letterBox = section.querySelector('.letter-html');
    if (letterBox) {
      letterBox.innerHTML = data?.letter?.html_message || 'Message failed to preview.';
    }
    const blocked = data.letter.disallowed_recipients?.join(', ');
    modal
      .querySelectorAll('.complainant.blocked-email-hideshow')
      .forEach(hideshow => (hideshow.hidden = !blocked || blocked.length <= 0));
  }

  function displayAgencyDetails(modal, data) {
    const section = modal.querySelector('.agency-letter');

    modal.querySelectorAll('.agency-name').forEach(nameContainer => {
      nameContainer.innerText = data?.referral_contact?.name || 'N/A';
    });

    if (!data?.letter) return;

    const letterBox = section.querySelector('.letter-html');
    if (letterBox) letterBox.innerHTML = data.letter.html_message;

    const yesEmails = document.querySelectorAll('.yes-agency-email');
    const noEmails = document.querySelectorAll('.no-agency-email');

    const allRecipients = [
      ...(data.letter.recipients || []),
      ...(data.letter.disallowed_recipients || [])
    ];

    if (!allRecipients.length) {
      noEmails.forEach(noEmail => (noEmail.hidden = false));
      yesEmails.forEach(yesEmail => (yesEmail.hidden = true));
      return;
    }
    noEmails.forEach(noEmail => (noEmail.hidden = true));
    yesEmails.forEach(yesEmail => (yesEmail.hidden = false));

    modal.querySelectorAll('.agency.email').forEach(e => (e.innerText = allRecipients[0] || ''));
    modal.querySelectorAll('.agency.subject').forEach(e => (e.innerText = data.letter.subject));
    const ccs = allRecipients.slice(1).join(', ');
    modal.querySelectorAll('.agency.ccs').forEach(e => (e.innerText = ccs || ''));

    const blocked = data.letter.disallowed_recipients?.join(', ');
    modal
      .querySelectorAll('.agency.blocked-email-hideshow')
      .forEach(hideshow => (hideshow.hidden = !blocked || blocked.length <= 0));
    modal.querySelectorAll('.agency.blocked-email').forEach(e => (e.innerText = blocked || ''));
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

  function initCancel(modal) {
    const cancelButton = getCloseModalButton(modal);
    root.CRT.cancelModal(modal, cancelButton, undefined, () => {
      reset(modal);
      modal.querySelector('.progress .steps').dataset.currentStep = 1;
      root.CRT.renderSteps(modal, validateModal);
    });
  }

  function updateCanClose(modal) {
    const sentToSoFar = [modal.dataset.repliedagency, modal.dataset.repliedcomplainant].filter(
      recipient => !!recipient
    );
    const numberSentSoFar = sentToSoFar.length;
    const notYetSentTo = ['agency', 'complainant'].filter(recipient => {
      return !sentToSoFar.includes(recipient);
    });

    if (numberSentSoFar === 1) {
      modal.dataset.confirmClose =
        `You've replied to the ${sentToSoFar[0]}` +
        ` but haven't contacted the ${notYetSentTo[0]}.` +
        ' Are you sure you want to exit without contacting both?';
    } else {
      modal.dataset.confirmClose = '';
    }

    if (numberSentSoFar === 2) {
      root.CRT.prepareToClose(modal);
    }
  }

  function downloadBase64Pdf(filename, content) {
    const pdfLink = document.createElement('a');
    pdfLink.setAttribute('download', `${filename}.pdf`);
    pdfLink.href = `data:application/pdf;base64,${content}`;
    pdfLink.click();
    pdfLink.remove();
  }

  function onReply(modal, button, action) {
    const actions = button.closest('.actions');
    const templateId = button.closest('form').querySelector('.template-field select').value;
    const reportId = getReportId();
    const publicId = getPublicId();
    const sectionClass = button.closest('.modal-step-content').classList;
    let recipient;
    if (sectionClass.contains('agency')) recipient = 'agency';
    else if (sectionClass.contains('complainant')) recipient = 'complainant';
    modal.dataset[`replied${recipient}`] = recipient;
    updateCanClose(modal);

    root.CRT.handleReferral(action, {
      reportId,
      responseTemplate: templateId,
      recipient
    })
      .then(({ data, status }) => {
        const tag = status >= 300 ? 'error' : 'success';
        root.CRT.showMessage(actions, { tag, content: data.response });
        if (tag !== 'success') return;
        if (data.pdf) downloadBase64Pdf(`Report ${publicId} (${recipient})`, data.pdf);
        button.disabled = true;
        // We need to refresh to show the updated action log:
        modal.dataset.navigateOnClose = `/form/view/${reportId}`;
      })
      .catch(error => {
        console.error(error);
        root.CRT.showMessage(actions, {
          tag: 'error',
          content: error?.response || 'Action failed unexpectedly.'
        });
      });
  }

  function initReply(modal, action) {
    const buttons = modal.querySelectorAll(`button.${action}`);
    buttons.forEach(button => {
      button.addEventListener('click', () => onReply(modal, button, action));
    });
  }

  function initActions(modal) {
    const openButton = getOpenModalButton();
    if (!openButton || !modal) return;
    openButton.addEventListener('click', event => showModal(event, modal));
    initCancel(modal);
    initReply(modal, 'send');
    initReply(modal, 'print');
  }

  function initModal() {
    const modal = getModal();
    initLanguage(modal);
    initAgencySelect(modal);
    initActions(modal);
    root.CRT.renderSteps(modal, validateModal);
  }

  initModal();
})(window);
