(function() {
  var previous_onkeydown = document.onkeydown;

  var modal = document.getElementById("intake_template");

  function openModal() {
    modal.removeAttribute("hidden");
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
  }

  function closeModal() {
    modal.setAttribute("hidden", "hidden");
    document.onkeydown = previous_onkeydown;
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

  var options = document.getElementById("intake_select");
  var letter = document.getElementById("intake_letter");
  var description = document.getElementById("intake_description");
  options.onchange = function(event) {
    event.preventDefault();
    var option = event.target.options[event.target.selectedIndex];
    description.innerHTML = option.dataset["description"];
    letter.innerHTML = option.dataset["content"];
  };
})();
