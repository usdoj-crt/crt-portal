(function(root, dom) {
  root.CRT = root.CRT || {};

  var previousOnkeydown = dom.onkeydown;
  var focusableElements =
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  root.CRT.openModal = function(modalEl) {
    dom.onkeydown = function(event) {
      event = event || window.event;
      var isEscape = false;
      if ('key' in event) {
        isEscape = event.key === 'Escape' || event.key === 'Esc';
      } else {
        isEscape = event.keyCode === 27;
      }
      if (isEscape) {
        root.CRT.closeModal(modalEl);
      }
      var isTab = false;
      if ('key' in event) {
        isTab = event.key === 'Tab';
      } else {
        isTab = event.keyCode === 9;
      }
      if (isTab) {
        var first = modalEl.querySelectorAll(focusableElements)[0];
        var focusableContent = modalEl.querySelectorAll(focusableElements);
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
    modalEl.removeAttribute('hidden');
    // get first input in this modal so we can focus on it
    var first = modalEl.querySelectorAll(focusableElements)[0];
    first.focus();
    dom.body.classList.add('is-modal');
  };

  root.CRT.closeModal = function(modalEl) {
    dom.onkeydown = previousOnkeydown;
    modalEl.setAttribute('hidden', 'hidden');
    dom.body.classList.remove('is-modal');
  };

  root.CRT.cancelModal = function(modalEl, cancelEl, formEl) {
    var dismissModal = function(event) {
      if (formEl) {
        formEl.scrollIntoView({ behavior: 'smooth', block: 'end', inline: 'nearest' });
        formEl.focus();
      }
      event.preventDefault();
      root.CRT.closeModal(modalEl);
    };
    cancelEl.addEventListener('click', dismissModal);
  };

  let nextStepIdPrefix = 1;
  root.CRT.refreshSteps = function(modalEl) {
    if (!modalEl.dataset.stepIdPrefix) {
      modalEl.dataset.stepIdPrefix = nextStepIdPrefix;
      nextStepIdPrefix++;
    }
    const stepIdPrefix = modalEl.dataset.stepIdPrefix;
    stepNavs = modalEl.querySelector('div[aria-label="progress"] .steps');
    const container = stepNavs.parentElement;

    [...container.querySelectorAll('.connecting-line')].forEach(line =>
      container.removeChild(line)
    );
    stepNavs.innerHTML = '';
    stepPages = modalEl.querySelectorAll('.modal-step');

    [...stepPages]
      .sort(function(a, b) {
        return a.dataset.step - b.dataset.step;
      })
      .forEach(function(stepPage) {
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

        const connectingLine = dom.createElement('div');
        if (stepNumber < stepPages.length) {
          connectingLine.classList.add('connecting-line');
          connectingLine.style.width = `calc(100% / ${stepPages.length -
            1} - (90px /  ${stepPages.length - 1}))`;
          container.prepend(connectingLine);
        }

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

        stepNavs.setAttribute('role', 'tablist');
        stepNav.setAttribute('aria-label', stepText.innerText);
        stepNav.setAttribute('role', 'tab');
        stepPage.setAttribute('role', 'tabpanel');
        stepNav.setAttribute('aria-controls', stepPage.id);
        stepPage.setAttribute('aria-labelledby', stepNav.id);
        stepNav.setAttribute('tabindex', '0');

        stepNav.addEventListener('click', function() {
          stepNavs.dataset.currentStep = stepNumber;
          root.CRT.refreshSteps(modalEl);
        });
        stepNav.addEventListener('keypress', function(event) {
          if (!['Enter', ' '].includes(event.key)) return;
          stepNavs.dataset.currentStep = stepNumber;
          root.CRT.refreshSteps(modalEl);
        });

        stepNavs.appendChild(stepNav);
      });
    stepNavs.querySelector('.current').focus();
  };
})(window, document);
