(function(root, dom) {
  var complaint_page = document.querySelector('.complaint-show-body');
  var option_mapping_to_section = {
    id_options_0: '.crt-correspondent-card',
    id_options_1: '.crt-report-card',
    id_options_2: '.crt-description-card',
    id_options_3: '.crt-comments-card',
    id_options_4: '.crt-summary-card',
    id_options_5: '.crt-activities-card'
  };

  var modal = document.getElementById('print_report');
  var original_beforeprint = root.onbeforeprint;
  var original_afterprint = root.onafterprint;
  var showModal = function(event) {
    event.preventDefault();
    if (modal.getAttribute('hidden') !== null) {
      // set up before and after print handlers so that we can
      // selectively hide or show sections.
      root.onbeforeprint = function(event) {
        for (var option_id in option_mapping_to_section) {
          var el = document.getElementById(option_id);
          var classname = option_mapping_to_section[option_id];
          var section = complaint_page.querySelector(classname);
          if (!el.checked) {
            section.setAttribute('hidden', 'hidden');
          }
        }
      };
      root.onafterprint = function(event) {
        for (var option_id in option_mapping_to_section) {
          var el = document.getElementById(option_id);
          var classname = option_mapping_to_section[option_id];
          var section = complaint_page.querySelector(classname);
          if (!el.checked) {
            section.removeAttribute('hidden');
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
  var print_button = document.getElementById('do_print_report');
  for (var option_id in option_mapping_to_section) {
    var el = document.getElementById(option_id);
    el.onclick = function(event) {
      var selected = modal.querySelectorAll('input[type=checkbox]:checked');
      if (selected.length == 0) {
        print_button.setAttribute('disabled', 'disabled');
      } else {
        print_button.removeAttribute('disabled');
      }
    };
  }

  print_button.onclick = function(event) {
    // hide the modal lest we print the modal itself.
    dom.body.classList.remove('is-modal');
    modal.setAttribute('hidden', 'hidden');
    root.print();
  };
})(window, document);
