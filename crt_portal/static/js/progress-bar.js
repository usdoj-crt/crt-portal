(function() {
  // see if we're in a browser that supports smooth scrolling, aka not IE11 and some versions of Edge
  // from https://stackoverflow.com/a/53672870
  function supportsSmoothScroll() {
    var supportsScroll = false;
    try {
      var div = document.createElement('div');
      div.scrollTo({
        top: 0,
        get behavior() {
          supportsScroll = true;
          return 'smooth';
        }
      });
    } catch (err) {
      console.log(err);
    }
    return supportsScroll;
  }

  if (supportsSmoothScroll() == true) {
    // enable smooth scroll with position:sticky header for browsers that support it
    var offsetHeight = document
      .getElementsByClassName('intake-header--progress-bar')[0]
      .getBoundingClientRect().height;
    var steps = document.getElementsByClassName('step');
    function smoothScroll(el) {
      el.preventDefault();
      var scrollToSection = document.getElementById(el.target.attributes.href.nodeValue.slice(1));
      var targetTop = scrollToSection.getBoundingClientRect().top;
      var totalOffset = targetTop - offsetHeight - 40; // 40px == padding on card, so title doesn't abut header
      window.scroll({
        top: window.pageYOffset + totalOffset,
        left: window.pageXOffset,
        behavior: 'smooth'
      });
    }
    for (i = 0; i < steps.length; i++) {
      steps[i].addEventListener('click', function(el) {
        smoothScroll(el);
      });
    }
  } else {
    // if browser doesn't support scrolling and position: sticky, use position: fixed instead
    var header = document.getElementsByClassName('intake-header')[0];
    var barOffset = header.getBoundingClientRect().height;
    var bar = document.getElementsByClassName('intake-header--progress-bar')[0];
    var cards = document.getElementsByClassName('crt-portal-card');

    window.addEventListener('scroll', function() {
      if (window.pageYOffset >= barOffset) {
        bar.style.position = 'fixed';
      } else {
        bar.style.position = 'relative'; // un-stick it when page is scrolled all the way up
      }
    });

    // add the class that keeps the card title from getting hidden under the fixed header
    for (i = 0; i < cards.length; i++) {
      cards[i].className = cards[i].className + ' crt-portal-card--space-for-header';
    }
  }
})(window);
