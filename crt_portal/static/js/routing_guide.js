(function(root) {
  let routingPrintButton = document.getElementsByClassName('routing-guide-print-button');
  if (routingPrintButton && routingPrintButton.length) {
    routingPrintButton[0].addEventListener('click', () => window.print());
  }
})(window);
