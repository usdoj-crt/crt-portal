(function(root) {
  const TOURS = {
    example: {
      title: 'Example walkthrough',
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
    },

    'setup-referral-contact': {
      title: 'Set up referrals to a new agency',
      steps: [
        {
          id: '1',
          title: 'Adding a referral contact - overview',
          text: `
              <p>Adding a referral contact consists of a few steps:</p>
              <ol>
                <li>Update the template content and send it to developers.</li>
                <li>Fill out the ReferralContact in the admin panel.</li>
                <li>Pair the ResponseTemplate with the ReferralContact.</li>
              </ol>
              <p>We'll start by looking at how to update the template content.</p>
              <p>This walkthrough will take us through a few existing objects - <strong>don't edit those directly</strong>, but feel free to <a href="/admin/" target="_blank">open a new tab</a> to be able to fill things in as we go.</p>
            `,
          mustBeOnUrl: '/admin/',
          when: {
            show: () => {
              document.querySelectorAll('tr.model-responsetemplate a').forEach(link => {
                link.href =
                  '/admin/cts_forms/responsetemplate/?title__icontains=Dept%20of%20ed%20referral%20form&admin-tour=setup-referral-contact&admin-tour-step=2';
              });
            }
          },
          attachTo: {
            element: 'tr.model-responsetemplate',
            scrollTo: true
          }
        },
        {
          id: '2',
          title: 'Adding a referral contact - workshopping the template',
          text: `
              <p>Here we can see some existing Referral templates.</p>
              <p>Let's take a look at this first template as an example.</p>
            `,
          when: {
            show: () => {
              const toBeClicked = document.querySelector('#result_list tr th a');
              toBeClicked.href += '&admin-tour=setup-referral-contact&admin-tour-step=3';
            }
          },
          nextAction: () => {
            document.querySelector('#result_list tr th a').click();
          },
          mustBeOnUrl:
            '/admin/cts_forms/responsetemplate/?title__icontains=dept%20of%20ed%20referral%20form',
          attachTo: {
            element: '#result_list tr th a',
            scrollTo: true
          }
        },
        {
          id: '3',
          title: 'Adding a referral contact - workshopping the template',
          text: `
              <p>Just as this template has, we need to add a {{ referral_text }} reference in our template's content.</p>
              <p>This will display the translated "Variable Text" that we'll fill out later on the Referral Contact - for example:</p>
<pre>Person Processing Referral
Department of Etc
1234 Fake Address Rd
Washington, D.C. 20420</pre>
          `,
          previousAction: () => {
            window.history.back();
          },
          attachTo: {
            element: '#id_body',
            scrollTo: true
          }
        },
        {
          id: '4',
          title: 'Adding a referral contact - workshopping the template',
          text: `
              <p>Updating the content in the "Body:" box will update this preview below.</p>
              <p>Once everything looks right, send the full content of this box to the dev team to add or update your new template.</p>
          `,
          attachTo: {
            element: '.field-preview',
            scrollTo: true
          }
        },
        {
          id: '5',
          title: 'Adding a referral contact - filling out the referral contact',
          text: `
              <p>Now that we've updated the template, we can move on to filling out the contact:</p>
              <ol>
                <li>Update the template content and send it to developers.</li>
                <li><strong>Fill out the ReferralContact in the admin panel.</strong></li>
                <li>Pair the ResponseTemplate with the ReferralContact.</li>
              </ol>
              <p>For that, we'll go to add a new ReferralContact.</p>
            `,
          mustBeOnUrl: '/admin/',
          nextAction: () => {
            document.querySelector('tr.model-referralcontact a.addlink').click();
          },
          previousAction: () => {
            window.history.back();
          },
          when: {
            show: () => {
              document.querySelectorAll('tr.model-referralcontact a.addlink').forEach(link => {
                link.href =
                  '/admin/cts_forms/referralcontact/add/?admin-tour=setup-referral-contact&admin-tour-step=6';
              });
            }
          },
          attachTo: {
            element: 'tr.model-referralcontact a.addlink',
            scrollTo: true
          }
        },
        {
          id: '6',
          title: 'Adding a referral contact - filling out the referral contact',
          text: `
              <p>Following the help text beneath each field, fill out the content and click SAVE</p>
          `,
          previousAction: () => {
            window.history.back();
          },
          attachTo: {
            element: '#content',
            scrollTo: true
          }
        },
        {
          id: '7',
          title: 'Adding a referral contact - pairing the response template',
          text: `
              <p>The last step is to tell our Response Template from part one about our Referral Contact from part two. This is how the application knows which agency to refer to based on a chosen template.</p>
              <ol>
                <li>Update the template content and send it to developers.</li>
                <li>Fill out the ReferralContact in the admin panel.</li>
                <li><strong>Pair the ResponseTemplate with the ReferralContact.</strong></li>
              </ol>
              <p>Let's look at an example of this on a random ResponseTemplate</p>
            `,
          mustBeOnUrl: '/admin/',
          previousAction: () => {
            window.history.back();
          }
        },
        {
          id: '8',
          title: 'Adding a referral contact - pairing the response template',
          text: `<p>Having navigated to our template, this field, Referral Contact, is all that's left to change.</p>
          <p>Once that's done, all that's left is to click save!</p>`,
          mustBeOnUrl: '/admin/cts_forms/responsetemplate/1/change/',
          attachTo: {
            element: '#id_referral_contact',
            scrollTo: true
          },
          previousAction: () => {
            window.history.back();
          }
        },
        {
          id: '9',
          title: 'Adding a referral contact - summary',
          text: `
              <p>And that's it! The steps again were:</p>
              <ol>
                <li>Update the template content and send it to developers.</li>
                <li>Fill out the ReferralContact in the admin panel.</li>
                <li>Pair the ResponseTemplate with the ReferralContact.</li>
              </ol>
              <p>At this point, a production release would be required for the template content to be made permanent. But, until then, content can be manually updated in dev to provide an end-to-end example of the new referral.</p>
            `,
          mustBeOnUrl: '/admin/',
          previousAction: () => {
            window.history.back();
          }
        }
      ]
    },

    'add-campaign': {
      title: 'Add a new outreach campaign',
      steps: [
        {
          id: '1',
          title: 'Add a new outreach campaign',
          text: `
              <p>Adding a new outreach campaign consists of a couple of steps:</p>
              <ol>
                <li><strong>Create the campaign</strong>.</li>
                <li>Create a shareable Shortened URL for the campaign.</li>
              </ol>
              <p>We'll start by creating the campaign.</p>
            `,
          mustBeOnUrl: '/admin/'
        },
        {
          id: '2',
          title: 'Create the campaign',
          text: `
              <p>To create the campaign, start by clicking "Add" next to Campaign.</p>
            `,
          mustBeOnUrl: '/admin/',
          nextAction: () => {
            document.querySelector('tr.model-campaign a.addlink').click();
          },
          when: {
            show: () => {
              document.querySelectorAll('tr.model-campaign a.addlink').forEach(link => {
                link.href =
                  '/admin/cts_forms/campaign/add/?admin-tour=add-campaign&admin-tour-step=3';
              });
            }
          },
          attachTo: {
            element: 'tr.model-campaign a.addlink',
            scrollTo: true
          }
        },
        {
          id: '3',
          title: 'Fill in campaign details',
          text: `
              <p>Fill in the campaign details</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/campaign/add/',
          attachTo: {
            element: '#content',
            scrollTo: true
          }
        },
        {
          id: '4',
          title: 'Click "Save and continue editing"',
          text: `
              <p>We want to stay on this page to create the URL, so select "Continue Editing"</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/campaign/add/',
          attachTo: {
            element: '.submit-row',
            scrollTo: true
          }
        },
        {
          id: '5',
          title: 'Create a shortened URL',
          text: `
              <p>Now that we've created the campaign, we can create a shortened URL for it.</p>
              <p>There's a shortcut from the campaign's own page that makes this easier - click "Create Short URL" to get started.</p>
            `,
          nextAction: () => {
            document.querySelector('.field-shorten_url a').click();
          },
          when: {
            show: () => {
              document.querySelector(
                '.field-shorten_url a'
              ).href += `&admin-tour=add-campaign&admin-tour-step=6`;
            }
          },
          attachTo: {
            element: '.field-shorten_url',
            scrollTo: true
          }
        },
        {
          id: '6',
          title: 'Provide a name for the URL',
          text: `
              <p>Because we've come via the shortcut, the destination is already filled in.</p>
              <p>Now we just need to provide a name for the URL.</p>
              <p>Note that you can only use letters, numbers, and dashes in the name.</p>
            `,
          attachTo: {
            element: '.field-shortname',
            scrollTo: true
          },
          previousAction: () => {
            window.history.back();
          }
        },
        {
          id: '7',
          title: 'Click "Save and continue editing"',
          text: `
              <p>We want to stay on this page, so select "Save and continue editing"</p>
            `,
          attachTo: {
            element: '.submit-row',
            scrollTo: true
          }
        },
        {
          id: '8',
          title: 'Done!',
          text: `
              <p>That's it! The campaign is now ready to be shared.</p>
              <p>To find the shareable URL, go back to the campaign you've just saved and look at the "Short URL" field. Viewing it there will account for differences in the production URL when sharing with the public versus internal staff.</p>
              <p>You can click "Copy to Clipboard" next to that link to copy it and share.</p>
            `,
          attachTo: {
            element: '.model-campaign',
            scrollTo: true
          },
          mustBeOnUrl: '/admin/'
        }
      ]
    },

    'add-saved-search': {
      title: 'Use Saved Search to reroute or refer reports',
      steps: [
        {
          id: '1',
          title: 'Overview',
          text: `
              <p>Saved Search allows admins to reroute or refer reports based on the content of the report.</p>
              <p>Let's look at an example of how to set this up.</p>
            `,
          mustBeOnUrl: '/admin/',
          attachTo: {
            element: '.model-savedsearch',
            scrollTo: true
          }
        },
        {
          id: '2',
          title: 'Create a new Saved Search',
          text: `
              <p>Start by clicking "Add" next to Saved Search.</p>
            `,
          mustBeOnUrl: '/admin/',
          nextAction: () => {
            document.querySelector('tr.model-savedsearch a.addlink').click();
          },
          when: {
            show: () => {
              document.querySelectorAll('tr.model-savedsearch a.addlink').forEach(link => {
                link.href =
                  '/admin/cts_forms/savedsearch/add/?admin-tour=add-saved-search&admin-tour-step=3';
              });
            }
          },
          attachTo: {
            element: 'tr.model-savedsearch a.addlink',
            scrollTo: true
          }
        },
        {
          id: '3',
          title: 'Add a name for the search',
          text: `
              <p>Now fill out the name.</p>
              <p>The name will appear in lists and dropdowns.</p>
              <p>For example, if a report is re-routed, the Saved Search that rerouted it will be named in the activity log.</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/savedsearch/add/',
          attachTo: {
            element: '.field-name',
            scrollTo: true
          }
        },
        {
          id: '4',
          title: 'Enter the query string for the saved search',
          text: `
              <p>The query string is the part of the URL after the question mark.</p>
              <p>For example, in the URL <code>https://civilrights.justice.gov/form/view/?status=new&status=open&no_status=false&grouping=default</code>, the query string is <code>status=new&status=open&no_status=false&grouping=default</code>.</p>
              <p>We'll double check this in a few steps, before activating the search.</p>
              <p><strong>Note:</strong> If you're confused about this at all, seek help from a developer - specifying an incorrect query may result in the saved search applying to too many records, or no records.</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/savedsearch/add/',
          attachTo: {
            element: '.field-query',
            scrollTo: true
          }
        },
        {
          id: '5',
          title: 'If setting up a referral - reason',
          text: `
              <p>If you're setting up a referral, you'll want to provide a reason for the referral.</p>
              <p>This will be recorded in the activity log.</p>
              <p>Otherwise, skip this step.</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/savedsearch/add/',
          attachTo: {
            element: '.field-auto_close_reason',
            scrollTo: true
          }
        },
        {
          id: '6',
          title: 'If setting up rerouting - section',
          text: `
              <p>If you're setting up rerouting, select the section to route to.</p>
              <p>Otherwise, skip this step.</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/savedsearch/add/',
          attachTo: {
            element: '.field-override_section_assignment_with',
            scrollTo: true
          }
        },
        {
          id: '7',
          title: 'Save and check results',
          text: `
              <p>Select "save and continue editing".</p>
              <p>This will allow us to stay on the same page and double check our results.</p>
              <p><strong>Note:</strong> Make sure you haven't checked the "Auto Close" or "Override Section Assignment" boxes yet. Saving now lets us double check that our search is correct before enabling the automatic action.</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/savedsearch/add/',
          attachTo: {
            element: '.submit-row',
            scrollTo: true
          }
        },
        {
          id: '8',
          title: 'Make sure the matching reports is correct',
          text: `
              <p>Take a look at the "View 1234 matching reports" count</p>
              <p>You can click through to make sure this filter will affect the correct reports</p>
              <p>Note that automatic action will only apply to <em>new reports</em> that come in while the search is active.</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/savedsearch/add/',
          attachTo: {
            element: '.field-matching_reports',
            scrollTo: true
          }
        },
        {
          id: '9',
          title: 'If setting up a referral - auto-close',
          text: `
              <p>Now that we've doubled checked, we can actually activate the search.</p>
              <p>If you're setting up a referral, you'll want to check the auto-close box so that records are not handled twice.</p>
              <p>Otherwise, skip this step.</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/savedsearch/add/',
          attachTo: {
            element: '.field-auto_close',
            scrollTo: true
          }
        },
        {
          id: '10',
          title: 'If setting up rerouting - override assignment',
          text: `
              <p>If you're setting up rerouting, check this box to turn on the auto-reassignment.</p>
              <p>Otherwise, skip this step.</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/savedsearch/add/',
          attachTo: {
            element: '.field-override_section_assignment',
            scrollTo: true
          }
        },
        {
          id: '11',
          title: 'Save and finish!',
          text: `
              <p>That's it! Select save to enable the search</p>
              <p>You can use the "View matching reports" link to double check the search as new reports come in.</p>
              <p>Note that automatic action will only apply to <em>new reports</em> that come in while the search is active.</p>
              <p>If you need to turn off the search, you can always come back and uncheck the "Auto Close" or "Override Section Assignment" boxes.</p>
            `,
          mustBeOnUrl: '/admin/cts_forms/savedsearch/add/',
          attachTo: {
            element: '.submit-row',
            scrollTo: true
          }
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

    return () => {
      const hasParams = stepToGoTo.mustBeOnUrl.includes('?') ? '&' : '?';
      window.location = `${stepToGoTo.mustBeOnUrl}${hasParams}admin-tour=${tourId}&admin-tour-step=${stepToGoTo.id}`;
    };
  }

  function getButtons(tour, tourId, step, currentStepIndex, steps) {
    const next = {
      text: 'Next',
      action: step.nextAction || getAction('next', tour, tourId, steps[currentStepIndex + 1])
    };

    const previous = {
      text: 'Previous',
      action: step.previousAction || getAction('back', tour, tourId, steps[currentStepIndex - 1])
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
        title: `${stepCountPrefix} ${step.title}`,
        classes: `shepherd-step-number-${index + 1}`
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
      row.dataset.tour = tourId;
      row.innerHTML = `
        <th scope="row">
          <a class="start-tour" href="javascript:void(0)">${tour.title}</a>
        </th>
        <td>
          <a class="viewlink start-tour" href="javascript:void(0)" class="viewlink">
            Start Walkthrough
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
