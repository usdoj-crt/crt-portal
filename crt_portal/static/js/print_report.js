((root, dom) => {
  const complaintPage = document.querySelector('.complaint-show-body');
  const OPTION_MAPPING_TO_SECTION = {
    id_options_0: '.crt-correspondent-card',
    id_options_1: '.crt-report-card',
    id_options_2: '.crt-description-card',
    id_options_3: '.crt-activities-card',
    id_options_4: '.crt-summary-card'
  };
  const ALWAYS_HIDE = ['.crt-outreach-card'];

  const modal = document.getElementById('print_report');
  const originalBeforeprint = root.onbeforeprint;
  const originalAfterprint = root.onafterprint;
  const showModal = event => {
    event.preventDefault();

    if (modal.getAttribute('hidden') === null) {
      root.onbeforeprint = originalBeforeprint;
      root.onafterprint = originalAfterprint;
      root.CRT.closeModal(modal);
      return;
    }

    root.onbeforeprint = event => {
      Object.entries(OPTION_MAPPING_TO_SECTION).forEach(([optionId, className]) => {
        const el = document.getElementById(optionId);
        if (el.checked) return;

        const sections = complaintPage.querySelectorAll(className);
        sections.forEach(section => {
          section.setAttribute('hidden', 'hidden');
        });
      });

      ALWAYS_HIDE.forEach(className => {
        complaintPage.querySelectorAll(className).forEach(toHide => {
          toHide.setAttribute('hidden', 'hidden');
        });
      });
    };

    root.onafterprint = event => {
      Object.entries(OPTION_MAPPING_TO_SECTION).forEach(([optionId, className]) => {
        const el = document.getElementById(optionId);
        const sections = complaintPage.querySelectorAll(className);
        if (el.checked) return;

        sections.forEach(section => {
          section.removeAttribute('hidden');
        });
      });
    };
    root.CRT.openModal(modal);
  };

  const report = document.getElementById('printout_report');
  report.addEventListener('click', showModal);

  const cancelModal = document.getElementById('print_report_cancel');
  root.CRT.cancelModal(modal, cancelModal);

  const printButtons = document.querySelectorAll('.print-report-button');
  Object.keys(OPTION_MAPPING_TO_SECTION).forEach(optionId => {
    const el = document.getElementById(optionId);
    el.onclick = event => {
      const selected = modal.querySelectorAll('input[type=checkbox]:checked');
      printButtons.forEach(printButton => {
        if (selected.length == 0) {
          printButton.setAttribute('disabled', 'disabled');
        } else {
          printButton.removeAttribute('disabled');
        }
      });
    };
  });

  printButtons.forEach(printButton => {
    printButton.onclick = event => {
      const printAll = event.target.value === 'print_all';
      const extraReports = document.querySelectorAll('.bulk-print-report-extra');
      extraReports.forEach(extraReport => {
        if (printAll) {
          extraReport.removeAttribute('hidden');
        } else {
          extraReport.setAttribute('hidden', 'hidden');
        }
      });
      dom.body.classList.remove('is-modal');
      modal.setAttribute('hidden', 'hidden');
      root.print();
    };
  });
})(window, document);
