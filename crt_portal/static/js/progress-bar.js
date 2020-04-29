(function() {
  var offsetHeight = document.getElementsByClassName('intake-header--progress-bar')[0].getBoundingClientRect().height;
  var steps = document.getElementsByClassName('step');
  function smoothScroll(el) {
    el.preventDefault();
    var scrollToSection = document.getElementById(el.target.attributes.href.nodeValue.slice(1, ));
    var targetTop = scrollToSection.getBoundingClientRect().top;
    var totalOffset = targetTop - offsetHeight - 40; // 40px == padding on card, so title doesn't abut header
    window.scroll({
      top: window.pageYOffset + totalOffset, 
      left: window.pageXOffset, 
      behavior: 'smooth'
    });
  };
  for (i=0; i<steps.length; i++){
    steps[i].addEventListener('click', function(el) {
      smoothScroll(el)
    });
  }
}(window));