(function(root, dom) {
  root.CRT = root.CRT || {};

  var previousOnkeydown = dom.onkeydown;
  var focusableElements =
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  root.CRT.openModal = function(modal) {
    dom.onkeydown = function(event) {
      event = event || window.event;
      var isEscape = false;
      if ('key' in event) {
        isEscape = event.key === 'Escape' || event.key === 'Esc';
      } else {
        isEscape = event.keyCode === 27;
      }
      if (isEscape) {
        root.CRT.closeModal(modal);
      }
      var isTab = false;
      if ('key' in event) {
        isTab = event.key === 'Tab';
      } else {
        isTab = event.keyCode === 9;
      }
      if (isTab) {
        var first = modal.querySelectorAll(focusableElements)[0];
        var focusableContent = modal.querySelectorAll(focusableElements);
        var last = focusableContent[focusableContent.length - 1];
        if (event.shiftKey) {
          // browse clickable elements moving backwards
          if (document.activeElement === first) {
            last.focus();
            event.preventDefault();
          }
        } else {
          // browse clickable elements moving forwards
          if (document.activeElement === last) {
            first.focus();
            event.preventDefault();
          }
        }
      }
    };
    modal.removeAttribute('hidden');
    // get first input in this modal so we can focus on it
    var first = modal.querySelectorAll(focusableElements)[0];
    first.focus();
    dom.body.classList.add('is-modal');
  };

  root.CRT.closeModal = function(modal) {
    dom.onkeydown = previousOnkeydown;
    modal.setAttribute('hidden', 'hidden');
    dom.body.classList.remove('is-modal');
  };

  root.CRT.cancelModal = function(modal, cancelEl, formEl) {
    var dismissModal = function(event) {
      if (formEl) {
        formEl.scrollIntoView({ behavior: 'smooth', block: 'end', inline: 'nearest' });
        formEl.focus();
      }
      event.preventDefault();
      root.CRT.closeModal(modal);
    };
    onUseButton(cancelEl, dismissModal);
  };

  let nextStepIdPrefix = 1;
  /** Initializes a modal with a series of steps.
   *
   * @param {HTMLElement} modal - The modal element.
   * @param {function} validateModal - A function(modal, {currentStep, targetStep}) that returns true/false and displays errors whether the modal can move to the given target step based on the state of the currentStep.
   *
   */
  root.CRT.renderSteps = function(modal, validateModal) {
    if (!modal.dataset.stepIdPrefix) {
      modal.dataset.stepIdPrefix = nextStepIdPrefix;
      nextStepIdPrefix++;
    }
    const stepIdPrefix = modal.dataset.stepIdPrefix;
    stepNavs = getProgress(modal);
    const container = stepNavs.parentElement;

    [...container.querySelectorAll('.connecting-line')].forEach(line =>
      container.removeChild(line)
    );
    stepNavs.innerHTML = '';
    stepPages = modal.querySelectorAll('.modal-step');

    [...stepPages]
      .sort(function(a, b) {
        return a.dataset.step - b.dataset.step;
      })
      .forEach((stepPage, _, stepPages) => {
        const context = {
          modal,
          validateModal,
          stepIdPrefix,
          stepPage,
          stepPages,
          stepNavs,
          container
        };
        initStepPage(context);
      });

    stepNavs.querySelector('.current').focus();
    setupSteps({ modal, validateModal });
  };

  function setupSteps({ modal, validateModal }) {
    if (modal.dataset.stepsInitialized) return;

    onUseButton(modal.querySelector('button.next'), () => {
      const steps = getProgress(modal);
      const currentStep = Number(steps.dataset.currentStep);
      const targetStep = currentStep + 1;
      goToStep({ modal, targetStep, validateModal });
    });

    modal.dataset.stepsInitialized = true;
  }

  function getProgress(modal) {
    return modal.querySelector('.progress .steps');
  }

  function initStepPage({
    modal,
    validateModal,
    stepIdPrefix,
    stepPage,
    stepPages,
    stepNavs,
    container
  }) {
    const stepNumber = Number(stepPage.dataset.step);
    const currentStepNumber = Number(stepNavs.dataset.currentStep);

    const stepNav = dom.createElement('li');
    stepNav.id = `modal-step-nav-${stepIdPrefix}-${stepNumber}`;
    stepPage.id = `modal-step-page-${stepIdPrefix}-${stepNumber}`;
    stepNav.classList.add('step');
    stepNav.dataset.step = stepNumber;

    const stepText = dom.createElement('div');
    stepText.innerText = stepPage.querySelector('.step-text').innerText;
    stepText.classList.add('step-text');
    stepNav.appendChild(stepText);

    const context = {
      modal,
      validateModal,
      stepPage,
      stepNav,
      stepPages,
      stepNavs,
      container,
      stepNumber,
      currentStepNumber,
      stepText
    };

    const connectingLine = makeConnectingLine(context);
    updateVisibility({ connectingLine, ...context });
    makeStepAccessible(context);
    onUseButton(stepNav, () => goToStep({ targetStep: stepNumber, ...context }));

    stepNavs.appendChild(stepNav);
  }

  function updateVisibility({ stepPage, stepNav, connectingLine, currentStepNumber, stepNumber }) {
    if (currentStepNumber === stepNumber) {
      stepPage.removeAttribute('hidden');
      stepNav.setAttribute('aria-current', 'true');
      stepNav.setAttribute('aria-selected', 'true');
      stepNav.classList.add('current');
      stepNav.focus();
    } else {
      stepPage.setAttribute('hidden', 'hidden');
      stepNav.setAttribute('aria-current', 'false');
      stepNav.setAttribute('aria-selected', 'false');
    }

    if (currentStepNumber === stepNumber) {
      connectingLine.classList.add('current');
    } else if (currentStepNumber > stepNumber) {
      connectingLine.classList.add('completed');
    } else {
      connectingLine.classList.add('future');
    }
  }

  function makeConnectingLine({ container, stepPages, stepNumber }) {
    const connectingLine = dom.createElement('div');
    if (stepNumber < stepPages.length) {
      connectingLine.classList.add('connecting-line');
      connectingLine.style.width = `calc(100% / ${stepPages.length -
        1} - (90px /  ${stepPages.length - 1}))`;
      container.prepend(connectingLine);
    }
    return connectingLine;
  }

  function makeStepAccessible({ stepNavs, stepNav, stepPage, stepText }) {
    stepNavs.setAttribute('role', 'tablist');
    stepNav.setAttribute('aria-label', stepText);
    stepNav.setAttribute('role', 'tab');
    stepPage.setAttribute('role', 'tabpanel');
    stepNav.setAttribute('aria-controls', stepPage.id);
    stepPage.setAttribute('aria-labelledby', stepNav.id);
    stepNav.setAttribute('tabindex', '0');
  }

  function onUseButton(button, action) {
    button.addEventListener('click', action);
    button.addEventListener('keypress', function(event) {
      if (!['Enter', ' '].includes(event.key)) return;
      action();
    });
  }

  function canGoToStep({ modal, targetStep, validateModal }) {
    const steps = getProgress(modal);
    const numSteps = steps.querySelectorAll('.step').length;
    if (targetStep > numSteps) return false;
    const currentStep = Number(steps.dataset.currentStep);
    if (!validateModal(modal, { currentStep, targetStep }).canLeaveStep) return false;
    return true;
  }

  function goToStep({ modal, targetStep, validateModal }) {
    if (!canGoToStep({ modal, targetStep, validateModal })) return;
    getProgress(modal).dataset.currentStep = targetStep;
    root.CRT.renderSteps(modal, validateModal);
  }
})(window, document);
