(function(root) {
const tour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      classes: 'usa-modal shadow-2 center',
      scrollTo: true
    }
  });

  tour.addStep({
    id: 'first-step',
    text: 'This is the new disposition page.',
    attachTo: {
      element: '.intake-section-title',
      on: 'bottom'
    },
    classes: 'first-step',
    buttons: [
      {
        text: 'Next',
        action: tour.next
      }
    ]
  });

  tour.addStep({
    id: 'second-step',
    text: 'This is the new disposition table.',
    attachTo: {
      element: '.intake-table-header',
      on: 'top'
    },
    classes: 'second-step',
    buttons: [
      {
        text: 'Next',
        action: tour.next
      }
    ]
  });
  if(!localStorage.getItem('shepherd-tour')) {
        tour.start();
        localStorage.setItem('shepherd-tour', 'yes');
    }
})(window);