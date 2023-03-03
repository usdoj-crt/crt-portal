(function(root) {
  function addReferralAddress(referral_contact) {
    const addressee = document.getElementById('form-letterhead--addressee');
    const deptAddressee = document.getElementById('form-letterhead--dept-addressee');

    if (deptAddressee) {
      deptAddressee.remove();
    }

    if (!addressee) return;

    const addressee_text = referral_contact?.addressee_text;
    if (!addressee_text) return;

    const newDeptAddressee = document.createElement('p');
    newDeptAddressee.id = 'form-letterhead--dept-addressee';
    newDeptAddressee.innerText = addressee_text;

    addressee.parentNode.insertBefore(newDeptAddressee, addressee);
  }

  document.addEventListener('DOMContentLoaded', function() {
    // `marked` should be loaded in global context at this point.
    if (marked) {
      marked.setOptions({
        gfm: true,
        breaks: true
      });
    } else {
      console.error('marked.js parser not loaded');
    }
  });

  var modal = document.getElementById('intake_template');

  var contact = document.getElementById('contact_complainant');
  var showModal = function(event) {
    event.preventDefault();
    if (modal.getAttribute('hidden') !== null) {
      root.CRT.openModal(modal);
    } else {
      root.CRT.closeModal(modal);
    }
  };
  contact.addEventListener('click', showModal);

  var cancel_modal = document.getElementById('intake_template_cancel');
  root.CRT.cancelModal(modal, cancel_modal);

  var copy = document.getElementById('intake_copy');
  var print = document.getElementById('intake_print');
  var letter = document.getElementById('intake_letter');
  var letter_html = document.getElementById('intake_letter_html');
  var send_email = document.getElementById('intake_send');

  var email_enabled = document.getElementById('intake_send').dataset.emailEnabled === 'True';
  var has_contact_email = Boolean(document.getElementById('contact_email').dataset.email);

  var reset = function() {
    description.innerHTML = '(select a response template)';
    letter_html.innerHTML = '';
    letter_html.hidden = true;
    letter.innerHTML = '';
    letter.hidden = false;
    copy.setAttribute('disabled', 'disabled');
    print.setAttribute('disabled', 'disabled');
    send_email.setAttribute('disabled', 'disabled');
  };

  const description = document.getElementById('intake_description');
  const options = document.getElementById('intake_select');
  const reportId = document.getElementById('template-report-id').value;
  options.addEventListener('change', function(event) {
    event.preventDefault();
    const index = event.target.selectedIndex;
    const option = event.target.options[index];
    const value = event.target.value;
    window
      .fetch('/api/responses/' + value + '/?report_id=' + reportId)
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        description.innerHTML = data.subject || '(select a response template)';
        if (data.is_html) {
          letter.hidden = true;
          letter_html.hidden = false;
          letter_html.innerHTML = marked.parse(data.body || '');
        } else {
          letter_html.hidden = true;
          letter.hidden = false;
          letter.innerHTML = data.body || '';
        }
        addReferralAddress(data.referral_contact);
      });
    if (index >= 1) {
      copy.removeAttribute('disabled');
      print.removeAttribute('disabled');
      if (email_enabled && has_contact_email) {
        send_email.removeAttribute('disabled');
      }
    } else {
      reset();
    }
  });

  var setLanguageCookie = function(lang) {
    document.cookie = 'form-letter-language' + '=' + lang;
  };

  var getLanguageCookie = function() {
    var nameEQ = 'form-letter-language=';
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  };

  var applyTemplateLanguageFilter = function() {
    var language_select = document.getElementById('template-language-select');
    var selected_language = language_select.value;

    // form letters for languages other than the one selected
    var toHide = document.querySelectorAll(
      `#intake_select > option.usa-select:not([data-language=${selected_language}])`
    );
    // form letters for the language that is selected
    var toShow = document.querySelectorAll(
      `#intake_select > option.usa-select[data-language=${selected_language}]`
    );

    for (var el of toHide) {
      el.setAttribute('hidden', 'true');
    }

    for (var el of toShow) {
      el.removeAttribute('hidden');
    }

    // the selected language changed, clear the currently selected form letter
    var intake_select = document.getElementById('intake_select');
    intake_select.selectedIndex = 0;
    reset();
  };

  var language_select = document.getElementById('template-language-select');
  language_select.onchange = function(event) {
    event.preventDefault();
    applyTemplateLanguageFilter();
    setLanguageCookie(language_select.value);
  };

  // try to grab the most recently used language setting
  if (getLanguageCookie()) {
    // if there is one, set the dropdown back to that value
    language_select.value = getLanguageCookie();
  }
  // refresh the template dropdown to reflect the current language selection
  applyTemplateLanguageFilter();

  function copyHTMLToClipboard(str) {
    function listener(e) {
      e.clipboardData.setData('text/html', str);
      e.clipboardData.setData('text/plain', str);
      e.preventDefault();
    }
    document.addEventListener('copy', listener);
    document.execCommand('copy');
    document.removeEventListener('copy', listener);
  }

  var copyContents = function(event) {
    // Text-only letter
    if (!letter.hidden) {
      const el = document.createElement('textarea');
      el.value = description.innerText + '\n\n' + letter.value;
      el.setAttribute('readonly', '');
      el.style.position = 'absolute';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      el.select();
      el.setSelectionRange(0, 99999); // mobile
      document.execCommand('copy');
      document.body.removeChild(el);
      // HTML content
    } else if (!letter_html.hidden) {
      copyHTMLToClipboard(letter_html.innerHTML);
    }
  };
  copy.addEventListener('click', copyContents);

  var printContents = function(event) {
    const letterhead = document.getElementById('form-letterhead');
    const letter_placeholder = document.getElementById('form-letter--placeholder');
    // Text-only letter
    if (!letter.hidden) {
      const el = document.createElement('p');
      el.append(letter.value);
      letter_placeholder.classList.add('form-letter-text');
      letter_placeholder.appendChild(el);
      // HTML letter
    } else if (!letter_html.hidden) {
      const el = letter_html.cloneNode(true);
      // Prevent id collision
      el.id = el.id + '_rand' + Math.floor(Math.random() * 1000000);
      letter_placeholder.appendChild(el);
    }
    letterhead.removeAttribute('hidden');
    document.body.appendChild(letterhead);
    window.print();
    letter_placeholder.classList.remove('form-letter-text');
    document.body.removeChild(letterhead);
    root.CRT.closeModal(modal);
  };
  print.addEventListener('click', printContents);
})(window);
