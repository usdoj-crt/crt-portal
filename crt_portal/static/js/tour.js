(function(root) {
  const dispositionTour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      cancelIcon: {
        enabled: true
      },
      classes: 'usa-modal shadow-2 center',
      scrollTo: true
    }
  });

  dispositionTour.addStep({
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
        action: dispositionTour.next
      }
    ]
  });

  dispositionTour.addStep({
    id: 'second-step',
    text:
      'The <strong>past disposition</strong> tab shows reports that are past their expiration date.',
    attachTo: {
      element: '.past-disposition',
      on: 'top'
    },
    classes: 'second-step',
    buttons: [
      {
        text: 'Next',
        action: dispositionTour.next
      }
    ]
  });

  dispositionTour.addStep({
    id: 'third-step',
    text:
      'The <strong>eligible for disposition</strong> tab shows reports that are within 30 days of or on their Expiration date.',
    attachTo: {
      element: '.eligible-expiration',
      on: 'top'
    },
    classes: 'third-step',
    buttons: [
      {
        text: 'Next',
        action: dispositionTour.next
      }
    ]
  });

  dispositionTour.addStep({
    id: 'fourth-step',
    text:
      'The <strong>other scheduled reports</strong> tab shows reports that have expiration dates more than 30 days in the future.',
    attachTo: {
      element: '.other-scheduled',
      on: 'top'
    },
    classes: 'fourth-step',
    buttons: [
      {
        text: 'Next',
        action: dispositionTour.next
      }
    ]
  });

  dispositionTour.addStep({
    id: 'fifth-step',
    text:
      'The record <strong>expiration date</strong> is the first of the year <strong>after</strong> the close date plus the number of years of the retention schedule.',
    attachTo: {
      element: '#expiration-date-sort',
      on: 'top'
    },
    classes: 'fifth-step',
    buttons: [
      {
        text: 'Next',
        action: dispositionTour.next
      }
    ]
  });

  dispositionTour.addStep({
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
        action: dispositionTour.next
      }
    ]
  });

  const savedSearchTour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      cancelIcon: {
        enabled: true
      },
      classes: 'usa-modal shadow-2 center',
      scrollTo: true
    }
  });

  savedSearchTour.addStep({
    id: 'first-step',
    text:
      'Welcome to Saved Searches! This feature will allow you to save Report Records table queries to share and return to later.',
    attachTo: {
      element: '.intake-section-title',
      on: 'top'
    },
    classes: 'first-step',
    buttons: [
      {
        text: 'Next',
        action: savedSearchTour.next
      }
    ]
  });

  savedSearchTour.addStep({
    id: 'second-step',
    text: 'Click this tab to view searches shared by other users.',
    attachTo: {
      element: '.shared-searches',
      on: 'bottom'
    },
    classes: 'second-step',
    buttons: [
      {
        text: 'Next',
        action: savedSearchTour.next
      }
    ]
  });

  savedSearchTour.addStep({
    id: 'third-step',
    text: 'Click this tab to view searches you created.',
    attachTo: {
      element: '.my-searches',
      on: 'bottom'
    },
    classes: 'third-step',
    buttons: [
      {
        text: 'Next',
        action: savedSearchTour.next
      }
    ]
  });

  savedSearchTour.addStep({
    id: 'fourth-step',
    text: 'Click the link to go to the Report Records table with the saved search filters applied.',
    attachTo: {
      element: '#name-sort',
      on: 'bottom'
    },
    classes: 'fourth-step',
    buttons: [
      {
        text: 'Done',
        action: savedSearchTour.next
      }
    ]
  });

  const savedSearchActionTour = new Shepherd.Tour({
    useModalOverlay: true,
    defaultStepOptions: {
      cancelIcon: {
        enabled: true
      },
      classes: 'usa-modal shadow-2 center',
      scrollTo: true
    }
  });

  savedSearchActionTour.addStep({
    id: 'first-step',
    text:
      'Add a new saved search here and it will appear in the "My saved searches tab" for future reference.',
    attachTo: {
      element: '.intake-section-title',
      on: 'top'
    },
    classes: 'first-step',
    buttons: [
      {
        text: 'Next',
        action: savedSearchActionTour.next
      }
    ]
  });

  savedSearchActionTour.addStep({
    id: 'second-step',
    text:
      'Add a user-friendly name and description to keep track of what this query is in reference to.',
    attachTo: {
      element: '#id_name',
      on: 'bottom'
    },
    classes: 'second-step',
    buttons: [
      {
        text: 'Next',
        action: savedSearchActionTour.next
      }
    ]
  });

  savedSearchActionTour.addStep({
    id: 'third-step',
    text: 'Add everything after the "?" in the url you want to save from the Report Records table.',
    attachTo: {
      element: '#id_query',
      on: 'bottom'
    },
    classes: 'third-step',
    buttons: [
      {
        text: 'Next',
        action: savedSearchActionTour.next
      }
    ]
  });

  savedSearchActionTour.addStep({
    id: 'fourth-step',
    text:
      'Check this box to make this search visible in the "Shared saved searches" tab to other portal users.',
    attachTo: {
      element: '#id_shared',
      on: 'bottom'
    },
    classes: 'fourth-step',
    buttons: [
      {
        text: 'Done',
        action: savedSearchActionTour.next
      }
    ]
  });

  const tours = [
    {
      localStorageName: 'disposition-tour',
      pagePath: '/form/disposition/',
      tourName: dispositionTour
    },
    {
      localStorageName: 'saved-search-tour',
      pagePath: '/form/saved-searches/',
      tourName: savedSearchTour
    },
    {
      localStorageName: 'saved-search-action-tour',
      pagePath: '/form/saved-searches/actions/new',
      tourName: savedSearchActionTour
    }
  ];

  function init() {
    const pathName = window.location.pathname;
    tours.forEach(tour => {
      if (localStorage.getItem(tour.localStorageName) != 'yes' && pathName == tour.pagePath) {
        tour.tourName.start();
        localStorage.setItem(tour.localStorageName, 'yes');
      }
    });
  }

  window.addEventListener('DOMContentLoaded', init);
})(window);
