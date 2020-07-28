(function(root) {
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
  contact.addEventListener('keydown', showModal);

  var cancel_modal = document.getElementById('intake_template_cancel');
  root.CRT.cancelModal(modal, cancel_modal);

  var copy = document.getElementById('intake_copy');
  var print = document.getElementById('intake_print');
  var letter = document.getElementById('intake_letter');
  var description = document.getElementById('intake_description');
  var options = document.getElementById('intake_select');
  options.onchange = function(event) {
    event.preventDefault();
    var index = event.target.selectedIndex;
    var option = event.target.options[index];
    description.innerHTML = option.dataset['description'] || '(select a response template)';
    letter.innerHTML = option.dataset['content'] || '';
    if (index >= 1) {
      copy.removeAttribute('disabled');
      print.removeAttribute('disabled');
    } else {
      copy.setAttribute('disabled', 'disabled');
      print.setAttribute('disabled', 'disabled');
    }
  };

  var copyContents = function(event) {
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
  };
  copy.addEventListener('click', copyContents);

  var printContents = function(event) {
    const el = document.createElement('p');
    el.classList.add('intake-letter-preview');
    el.append(letter.value);
    document.body.appendChild(el);
    window.print();
    document.body.removeChild(el);
    root.CRT.closeModal(modal);
  };
  print.addEventListener('click', printContents);
})(window);
