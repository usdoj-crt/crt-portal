(function() {
  var previous_onkeydown = document.onkeydown;

  var modal = document.getElementById("intake_template");

  function openModal() {
    document.onkeydown = function(event) {
      event = event || window.event;
      var isEscape = false;
      if ("key" in event) {
        isEscape = (event.key === "Escape" || event.key === "Esc");
      } else {
        isEscape = (event.keyCode === 27);
      }
      if (isEscape) {
        closeModal();
      }
    };
    modal.removeAttribute("hidden");
  }

  function closeModal() {
    document.onkeydown = previous_onkeydown;
    modal.setAttribute("hidden", "hidden");
  }

  var contact = document.getElementById("contact_complainant");
  contact.onclick = function(event) {
    event.preventDefault();
    if (modal.getAttribute("hidden") !== null) {
      openModal();
    } else {
      closeModal();
    }
  };

  var cancel_modal = document.getElementById("intake_template_cancel");
  cancel_modal.onclick = function(event) {
    event.preventDefault();
    closeModal();
  };

  var copy = document.getElementById("intake_copy");
  copy.onclick = function(event) {
    event.preventDefault();
  };

  var options = document.getElementById("intake_select");
  var letter = document.getElementById("intake_letter");
  var description = document.getElementById("intake_description");
  options.onchange = function(event) {
    event.preventDefault();
    var index = event.target.selectedIndex;
    var option = event.target.options[index];
    description.innerHTML = option.dataset["description"];
    letter.innerHTML = option.dataset["content"];
    if (index >= 1) {
      copy.removeAttribute("disabled");
    } else {
      copy.setAttribute("disabled", "disabled");
    }
  };
})();
