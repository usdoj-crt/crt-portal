(function(root) {
  let routingPrintButton = document.getElementsByClassName("routing-guide-print-button")
  console.log("routing-guide-print-button", routingPrintButton)
  if (routingPrintButton && routingPrintButton.length) {
    routingPrintButton[0].addEventListener('click', () => window.print())
  }
})(window);
