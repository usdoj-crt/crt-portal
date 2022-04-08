(function (root, dom) {
  var complaint_page = document.querySelector('.complaint-show-body');
  var option_mapping_to_section = {
    id_options_0: '.crt-correspondent-card',
    id_options_1: '.crt-report-card',
    id_options_2: '.crt-description-card',
    id_options_3: '.crt-activities-card',
    id_options_4: '.crt-summary-card',
  };

  var modal = document.getElementById('print_report');
  var original_beforeprint = root.onbeforeprint;
  var original_afterprint = root.onafterprint;
  var showModal = function (event) {
    event.preventDefault();
    if (modal.getAttribute('hidden') !== null) {
      // set up before and after print handlers so that we can
      // selectively hide or show sections.
      root.onbeforeprint = function (event) {
        for (var option_id in option_mapping_to_section) {
          var el = document.getElementById(option_id);
          var classname = option_mapping_to_section[option_id];
          var sections = complaint_page.querySelectorAll(classname);
          if (!el.checked) {
            sections.forEach(function (section) {
              section.setAttribute('hidden', 'hidden');
            });
          }
        }
      };
      root.onafterprint = function (event) {
        for (var option_id in option_mapping_to_section) {
          var el = document.getElementById(option_id);
          var classname = option_mapping_to_section[option_id];
          var sections = complaint_page.querySelectorAll(classname);
          if (!el.checked) {
            sections.forEach(function (section) {
              section.removeAttribute('hidden');
            });
          }
        }
      };
      root.CRT.openModal(modal);
    } else {
      // reset before and after print handlers.
      root.onbeforeprint = original_beforeprint;
      root.onafterprint = original_afterprint;
      root.CRT.closeModal(modal);
    }
  };

  var report = document.getElementById('printout_report');
  report.addEventListener('click', showModal);

  var cancel_modal = document.getElementById('print_report_cancel');
  root.CRT.cancelModal(modal, cancel_modal);

  // if no options are clicked, disable the print button.
  var print_buttons = document.querySelectorAll('.print-report-button');
  for (var option_id in option_mapping_to_section) {
    var el = document.getElementById(option_id);
    el.onclick = function (event) {
      var selected = modal.querySelectorAll('input[type=checkbox]:checked');
      for (var i = 0; i < print_buttons.length; i++) {
        var print_button = print_buttons[i];
        if (selected.length == 0) {
          print_button.setAttribute('disabled', 'disabled');
        } else {
          print_button.removeAttribute('disabled');
        }
      }
    };
  }

  for (var i = 0; i < print_buttons.length; i++) {
    var print_button = print_buttons[i];
    print_button.onclick = function (event) {
      // display extra reports only if user hits "print all"
      var print_all = event.target.value === 'print_all';
      var extra_reports = document.querySelectorAll('.bulk-print-report-extra');
      for (var j = 0; j < extra_reports.length; j++) {
        var report = extra_reports[j];
        if (print_all) {
          report.removeAttribute('hidden');
        } else {
          report.setAttribute('hidden', 'hidden');
        }
      }
      // hide the modal lest we print the modal itself.
      dom.body.classList.remove('is-modal');
      modal.setAttribute('hidden', 'hidden');
      root.print();
    };
  }
})(window, document);
