(function(root) {
  const TOURS = {
    example: {
      title: 'Example tour',
      steps: [
        {
          id: '1',
          title: 'First step',
          text: 'This is the first step. Pressing next will go to the next step.',
          mustBeOnUrl: '/admin/'
        },
        {
          id: '2',
          title: 'Second step',
          text: 'This is the second step. Pressing next will go to the users page.'
        },
        {
          id: '3',
          title: 'Third step',
          arrow: true,
          text:
            'This is the third step. It shows how to target a specific element, such as this username.',
          attachTo: {
            element: '.results tr:first-of-type .field-username'
          },
          mustBeOnUrl: '/admin/auth/user/'
        },
        {
          id: '4',
          title: 'Last step',
          arrow: true,
          text: 'This is the last step. It shows how you can scroll between elements on a page.',
          attachTo: {
            element: '#nav-sidebar .module:last-child',
            scrollTo: true
          },
          mustBeOnUrl: '/admin/auth/user/'
        }
      ]
    }
  };

  function getDefaultAction(direction, tour) {
    if (direction === 'next') return tour.next;
    if (direction === 'back') return tour.back;
    return tour.complete;
  }

  function getAction(direction, tour, tourId, stepToGoTo) {
    if (!stepToGoTo) return tour.complete;

    const defaultAction = getDefaultAction(direction, tour);
    if (!stepToGoTo.mustBeOnUrl) return defaultAction;
    if (window.location.pathname === stepToGoTo.mustBeOnUrl) {
      return defaultAction;
    }

    return () =>
      (window.location = `${stepToGoTo.mustBeOnUrl}?admin-tour=${tourId}&admin-tour-step=${stepToGoTo.id}`);
  }

  function getButtons(tour, tourId, step, currentStepIndex, steps) {
    const next = {
      text: 'Next',
      action: getAction('next', tour, tourId, steps[currentStepIndex + 1])
    };

    const previous = {
      text: 'Previous',
      action: getAction('back', tour, tourId, steps[currentStepIndex - 1])
    };

    const done = {
      text: 'Done',
      action: tour.complete
    };

    const cancel = {
      text: 'Cancel',
      action: tour.cancel
    };

    const asFirstStep = currentStepIndex === 0;
    const atLastStep = currentStepIndex === steps.length - 1;

    return [
      ...(atLastStep ? [done] : [cancel]),
      ...(atLastStep ? [] : [next]),
      ...(asFirstStep ? [] : [previous])
    ];
  }

  function startOrResumeTour() {
    const searchParams = new URLSearchParams(window.location.search);
    const tourId = searchParams.get('admin-tour');
    const stepId = searchParams.get('admin-tour-step');
    if (!tourId) return;
    const tourData = TOURS[tourId];
    if (!tourData) {
      console.error(`No tour found for ${tourId}`);
      return;
    }

    const tour = new Shepherd.Tour({
      defaultStepOptions: {
        scrollTo: true,
        showCancelLink: true
      }
    });

    const steps = tourData.steps;
    const currentStep = steps.find(step => step.id === stepId);

    steps.forEach((step, index) => {
      stepCountPrefix = `
        <span class="shepherd-step-count">
          ${index + 1}/${steps.length}
        </span>
      `;
      tour.addStep({
        buttons: getButtons(tour, tourId, step, index, steps),
        ...step,
        title: `${stepCountPrefix} ${step.title}`
      });
    });

    if (currentStep) {
      tour.show(currentStep.id);
      return;
    }
    tour.start();
  }

  function addTourLinks() {
    if (window.location.pathname !== '/admin/') return;

    const mainContent = document.querySelector('#content-main');
    if (!mainContent) return;

    const tourLinks = document.createElement('div');
    tourLinks.classList.add('module');
    tourLinks.innerHTML = `
      <table>
        <caption>
          <span>Walkthroughs</span>
        </caption>
        <tbody class="tours">
        </tbody>
      </table>
    `;
    const links = tourLinks.querySelector('.tours');

    Object.entries(TOURS).forEach(([tourId, tour]) => {
      const row = document.createElement('tr');
      row.classList.add('model-action');
      row.innerHTML = `
        <th scope="row">
          <a class="start-tour" href="javascript:void(0)">${tour.title}</a>
        </th>
        <td>
          <a class="viewlink start-tour" href="javascript:void(0)" class="viewlink">
            ${tour.title}
          </a>
        </td>
      `;

      row.querySelectorAll('.start-tour').forEach(link => {
        link.addEventListener('click', () => {
          window.location = `/admin/?admin-tour=${tourId}`;
        });
      });

      links.appendChild(row);
    });

    mainContent.prepend(tourLinks);
  }

  function init() {
    startOrResumeTour();
    addTourLinks();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window);
