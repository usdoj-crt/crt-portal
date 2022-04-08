(function () {
  var USA_INPUT_ERROR = 'usa-input--error';
  var inputs = document.querySelectorAll('input[type="text"], textarea, select');
  var inputList = Array.prototype.slice.call(inputs);

  function isRequired(node) {
    return node.required;
  }

  function removeError(event) {
    var node = event.target;

    node.classList.remove(USA_INPUT_ERROR);
  }
  inputList.filter(isRequired).forEach(function (node) {
    node.addEventListener('change', removeError);
  });
})();
