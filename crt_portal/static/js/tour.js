(function(root) {
  const tour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      cancelIcon: {
        enabled: true
      },
      classes: 'usa-modal shadow-2 center',
      scrollTo: true
    }
  });

  tour.addStep({
    id: 'first-step',
    title: 'Welcome to the new Records Disposition page!',
    text:
      "This page features tables of reports that are closed and have been assigned a retention schedule. The reports are subdivided by their expiration date relative to today's date.",
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
    text: 'The <b>past disposition</b> tab shows reports that are past their expiration date.',
    attachTo: {
      element: '.past-disposition',
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

  tour.addStep({
    id: 'third-step',
    text:
      'The <b>eligible for expiration</b> tab shows reports that are within 30 days of or on their Expiration date.',
    attachTo: {
      element: '.eligible-expiration',
      on: 'top'
    },
    classes: 'third-step',
    buttons: [
      {
        text: 'Next',
        action: tour.next
      }
    ]
  });

  tour.addStep({
    id: 'fourth-step',
    text:
      'The <b>other scheduled reports</b> tab shows reports that have expiration dates more than 30 days in the future.',
    attachTo: {
      element: '.other-scheduled',
      on: 'top'
    },
    classes: 'fourth-step',
    buttons: [
      {
        text: 'Next',
        action: tour.next
      }
    ]
  });

  tour.addStep({
    id: 'fifth-step',
    text:
      'The record <b>expiration date</b> is the close date plus number of years of the retention schedule.',
    attachTo: {
      element: '#expiration-date-sort',
      on: 'top'
    },
    classes: 'fifth-step',
    buttons: [
      {
        text: 'Next',
        action: tour.next
      }
    ]
  });

  tour.addStep({
    id: 'sixth-step',
    text:
      'In the future this page will allow users to generate a disposition form for eligible records and submit them for destruction.',
    attachTo: {
      element: '.intake-section-title',
      on: 'bottom'
    },
    classes: 'sixth-step',
    buttons: [
      {
        text: 'Done',
        action: tour.next
      }
    ]
  });

  if (!localStorage.getItem('shepherd-tour')) {
    tour.start();
    localStorage.setItem('shepherd-tour', 'yes');
  }
})(window);
