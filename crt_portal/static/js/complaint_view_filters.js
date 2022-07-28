(function(root, dom) {


  /**
   * Convert an array-like object to an array.
   *
   * NodeLists, such as those returned via a form's `elements`
   * property, can be accessed like arrays but are missing
   * their interation helpers. This allows us to call methods like
   * `.forEach` and `.map` on them.
   */
  function toArray(arrayLike) {
    return Array.prototype.slice.call(arrayLike);
  }

  // 'Box' an element in an array if it isn't one currently
  function wrapValue(maybeUnboxed) {
    return Array.isArray(maybeUnboxed) ? maybeUnboxed : [maybeUnboxed];
  }

  /**
   * Converts a query string into an object, where the key is the
   * name of the query and the value is an array of all values associated
   * with that query.
   *
   * Necessary because we can have multiple filters / search params
   * with the same name, and they all need to be passed in the final query.
   *
   * @param {String} queryString The query string we want to convert into an object
   * @param {Array} paramsWhitelist The list of params accepted as search filters
   * @returns {Object} Map of all params and their URL encoded values
   */
  function getQueryParams(queryString, paramsWhitelist) {
    let paramsMap = {};
    const search = new URLSearchParams(queryString);
    const acceptedParams = (paramsWhitelist instanceof Array && paramsWhitelist) || [];

    search.forEach(function(value, filterName) {
      if (acceptedParams.indexOf(filterName) >= 0) {
        paramsMap[filterName] = paramsMap[filterName] || [];

        if (paramsMap[filterName].indexOf(value) < 0) {
          paramsMap[filterName].push(encodeURIComponent(value));
        }
      }
    });

    return paramsMap;
  }

  /**
   * Given an object of query parameters, convert them back into a string
   * @param {Object} paramsObj The key/vslue pairs to be turned into query params
   * @returns {Array} A list of URI-encoded query param strings
   */
  function makeQueryParams(params) {
    let keys = Object.keys(params);
    return keys.reduce(function(memo, key) {
      const paramValue = params[key];

      if (!paramValue || !paramValue.length) {
        return memo;
      }

      let valueToList = wrapValue(paramValue);
      let paramsString = valueToList
        .reduce(function(accum, value) {
          accum.push(makeQueryParam(key, value));

          return accum;
        }, [])
        .join('&');

      memo.push(paramsString);

      return memo;
    }, []);
  }

  /**
   * Build a URI-encoded query paramater
   * @param {String} key The name of the query param
   * @param {String} value The value of the query param
   * @returns {String} Param in the format of {key}={value}
   */
  function makeQueryParam(key, value) {
    return key + '=' + encodeURIComponent(value);
  }

  /**
   * Concat all previous params together
   * @param {Array} params An array of URI-encoded query param strings
   * @returns {String} The strings joined as a single ampersand-delimited string
   */
  function finalizeQueryParams(params) {
    return params.length ? params.join('&') : '';
  }

  /**
   * filterDataModel and the mutation function below control the `model` behavior
   * of the filters
   */

  let initialFilterState = {
    status: [],
    location_state: [],
    primary_complaint: [],
    contact_first_name: '',
    contact_last_name: '',
    contact_email: '',
    violation_summary: [],
    location_name: '',
    location_address_line_1: '',
    location_address_line_2: '',
    location_city_town: '',
    create_date_start: '',
    create_date_end: '',
    summary: '',
    assigned_to: '',
    public_id: '',
    primary_statute: '',
    reported_reason: [],
    commercial_or_public_place: [],
    intake_format: [],
    servicemember: [],
    hate_crime: [],
    referred: [],
    sort: '',
    page: '',
    per_page: '',
    no_status: '',
    language: [],
    correctional_facility_type: []
  };
  let filterDataModel = {};

  /**
   * Mutate the current filter state with updated filter values
   * @param {Object} state The current filter state
   * @param {Object} updates The properties of the filter state to be updated
   */
  function mutateFilterDataWithUpdates(state, updates) {
    for (const [key, value] of Object.entries(updates)) {
      if (state.hasOwnProperty(key)) {
        state[key] = decodeFormData(value);
      }
    }
  }

  function decodeFormData(data) {
    if (Array.isArray(data)) {
      return data.map(decodeURIComponent);
    }
    return decodeURIComponent(data);
  }

  /**
   * The following functions represent the 'views' for this  application —
   * these are the components that wire up event handling behavior to
   * specific DOM nodes.
   *
   * Each view takes a `props` object, which, at a minimum, accepts an `el` property, which is
   * a pointer to the DOM node we want to add interactive behavior to.
   */

  /**
   * View to control filter tag behavior
   * @param {Object} props
   * @param {HTMLElement} props.el The DOM node this view manages
   */
  function filterTagView(props) {
    let filters = props.el;
    let onClickHandler = props.onClick;

    filters.addEventListener('click', function handleFilterTagClick(event) {
      const node = event.target;
      if (node.tagName === 'BUTTON') {
        onClickHandler(node);
      }
    });
  }

  /**
   * View to control form element
   * @param {Object} props
   * @param {HTMLElement} props.el The DOM node this view manages
   */
  function formView(props) {
    let form = props.el;

    form.addEventListener('submit', function handleSubmit(event) {
      event.preventDefault();

      formView.doSearch(form);
    });
  }

  /**
   * Create a query param string from our filter data model, and update the URL
   * in the browser to perform a new search with the applied filters
   */
  formView.doSearch = function doSearch(form) {
    const preparedFilters = finalizeQueryParams(makeQueryParams(filterDataModel));
    let finalQuery = '';
    if (preparedFilters) {
      finalQuery = '?' + preparedFilters;
    }
    window.location = form.action + finalQuery;
  };

  /**
   * View to control multiselect element behavior
   * @param {Object} props
   * @param {HTMLElement} props.el The DOM node this view manages
   */
  function multiSelectView(props) {
    props.el.addEventListener('change', function(event) {
      filterDataModel[props.name] = multiSelectView.getValues(event.target);
    });
  }

  multiSelectView.getValues = function(select) {
    let options = toArray((select && select.options) || []);

    function isSelected(option) {
      return option.selected;
    }

    function unwrapValue(x) {
      return x.value;
    }

    return options.filter(isSelected).map(unwrapValue);
  };

  function checkBoxView(props) {
    for (let i = 0; i < props.el.length; i++) {
      props.el[i].addEventListener('change', function(event) {
        checkBoxView.getValues(event.target);
      });
    }
  }

  checkBoxView.getValues = function(el) {
    if (el.checked) {
      filterDataModel[event.target.name].push(el.value);
    } else {
      const index = filterDataModel[event.target.name].indexOf(el.value);
      filterDataModel[event.target.name].splice(index, 1);
    }
  };

  /**
   * View to control text input element behavior
   * @param {Object} props
   * @param {HTMLElement} props.el The DOM node this view manages
   * @param {String} props.name The key in the filter data model that corresponds to the data to update
   */
  function textInputView(props) {
    if (!props.el || !props.name) {
      throw new Error(
        'Component must be supplied with a valid DOM node and a `name` key corresponding to a key in the filterDataModel object'
      );
    }

    props.el.addEventListener('change', function(event) {
      filterDataModel[props.name] = event.target.value;
      if (props.name == 'per_page') {
        dom.getElementById('apply-filters-button').click()
      }
    });
  }

  function clearFiltersView(props) {
    props.el.addEventListener('click', props.onClick);
  }

  function filterController() {
    const formEl = dom.getElementById('filters-form');
    const firstNameEl = formEl.querySelector('input[name="contact_first_name"');
    const lastNameEl = formEl.querySelector('input[name="contact_last_name"');
    const locationCityEl = formEl.querySelector('input[name="location_city_town"]');
    const locationNameEl = formEl.querySelector('input[name="location_name"]');
    const locationStateEl = dom.getElementsByName('location_state');
    const activeFiltersEl = dom.querySelector('[data-active-filters]');
    const clearAllEl = dom.querySelector('[data-clear-filters]');
    const statusEl = dom.getElementsByName('status');
    const summaryEl = formEl.querySelector('input[name="summary"]');
    const createDateStartEl = formEl.querySelector('input[name="create_date_start');
    const createDateEndEl = formEl.querySelector('input[name="create_date_end');
    const assigneeEl = formEl.querySelector('#id_assigned_to');
    const complaintIDEl = formEl.querySelector('input[name="public_id"');
    const statuteEl = formEl.querySelector('select[name="primary_statute"]');
    const perPageEl = formEl.querySelector('select[name="per_page"]');
    const personalDescriptionEl = formEl.querySelector('input[name="violation_summary"]');
    const primaryIssueEl = dom.getElementsByName('primary_complaint');
    const reportedReasonEl = dom.getElementsByName('reported_reason');
    const relevantDetailsEl = dom.getElementsByName('commercial_or_public_place');
    const intakeFormatEl = dom.getElementsByName('intake_format');
    const hateCrimeEl = dom.getElementsByName('hate_crime');
    const servicememberEl = dom.getElementsByName('servicemember');
    const contactEmailEl = dom.querySelector('input[name="contact_email"]');
    const referredEl = dom.getElementsByName('referred');
    const languageEl = dom.getElementsByName('language');
    const correctionalFacilityTypeEl = dom.getElementsByName('correctional_facility_type');
    /**
     * Update the filter data model when the user clears (clicks on) a filter tag,
     * and perform a new search with the updated filters applied.
     * @param {HTMLElement} node An HTML element
     */
    function onFilterTagClick(node) {
      const filterName = node.getAttribute('data-filter-name');

      // see if we have to process multiple select elements first
      const multiSelectElements = [
        'status',
        'location_state',
        'violation_summary',
        'primary_complaint',
        'intake_format',
        'commercial_or_public_place',
        'reported_reason',
        'language',
        'correctional_facility_type'
      ];
      const filterIndex = multiSelectElements.indexOf(filterName);
      if (filterIndex !== -1) {
        let selections = filterDataModel[filterName];
        const selectionData = node.getAttribute('data-filter-value');
        selections.splice(selections.indexOf(selectionData), 1);
        filterDataModel[filterName] = selections;
      } else {
        filterDataModel[filterName] = '';
      }

      formView.doSearch(formEl);
    }

    function clearAllFilters() {
      const activeFilters = toArray(activeFiltersEl.children);

      let updates = activeFilters.reduce(function(updates, node) {
        const filterName = node.getAttribute('data-filter-name');
        let currentFilterData = filterDataModel[filterName];
        currentFilterData = wrapValue(currentFilterData);
        if (currentFilterData.length) {
          updates[filterName] = initialFilterState[filterName];
        }

        return updates;
      }, {});

      mutateFilterDataWithUpdates(filterDataModel, updates);
      formView.doSearch(formEl);
    }

    formView({
      el: formEl
    });
    textInputView({
      el: firstNameEl,
      name: 'contact_first_name'
    });
    textInputView({
      el: lastNameEl,
      name: 'contact_last_name'
    });
    textInputView({
      el: locationCityEl,
      name: 'location_city_town'
    });
    textInputView({
      el: locationNameEl,
      name: 'location_name'
    });
    checkBoxView({
      el: locationStateEl,
      name: 'location_state'
    });
    filterTagView({
      el: activeFiltersEl,
      onClick: onFilterTagClick
    });
    checkBoxView({
      el: statusEl,
      name: 'status'
    });
    textInputView({
      el: summaryEl,
      name: 'summary'
    });
    textInputView({
      el: assigneeEl,
      name: 'assigned_to'
    });
    textInputView({
      el: personalDescriptionEl,
      name: 'violation_summary'
    });
    textInputView({
      el: createDateStartEl,
      name: 'create_date_start'
    });
    textInputView({
      el: createDateEndEl,
      name: 'create_date_end'
    });
    textInputView({
      el: complaintIDEl,
      name: 'public_id'
    });
    textInputView({
      el: statuteEl,
      name: 'primary_statute'
    });
    textInputView({
      el: perPageEl,
      name: 'per_page'
    });
    clearFiltersView({
      el: clearAllEl,
      onClick: clearAllFilters
    });
    checkBoxView({
      el: primaryIssueEl,
      name: 'primary_complaint'
    });
    checkBoxView({
      el: reportedReasonEl,
      name: 'reported_reason'
    });
    checkBoxView({
      el: relevantDetailsEl,
      name: 'commercial_or_public_place'
    });
    checkBoxView({
      el: intakeFormatEl,
      name: 'intake_format'
    });
    checkBoxView({
      el: hateCrimeEl,
      name: 'hate_crime'
    });
    checkBoxView({
      el: servicememberEl,
      name: 'servicemember'
    });
    textInputView({
      el: contactEmailEl,
      name: 'contact_email'
    });
    checkBoxView({
      el: referredEl,
      name: 'referred'
    });
    checkBoxView({
      el: languageEl,
      name: 'language'
    });
    checkBoxView({
      el: correctionalFacilityTypeEl,
      name: 'correctional_facility_type'
    });
  }

  function validateTextSearch(el) {
    let buttonEl = document.getElementById('apply-filters-button');
    let alertEl = document.getElementById('search-notification');
    let textEl = alertEl.querySelector('.usa-alert__text');
    const value = el.value;
    if (value.includes('(') && value.includes(')') && value.includes('"')) {
      buttonEl.setAttribute('disabled', '');
      textEl.textContent =
        '(Parentheses) and "quotation marks" cannot be used together in the same keyword search';
      alertEl.style.display = 'inline-block';
    } else {
      buttonEl.removeAttribute('disabled');
      textEl.textContent = '';
      alertEl.style.display = 'none';
    }
  }

  function initValidateTextSearch() {
    let inputEl = document.getElementById('id_violation_summary');
    // Validate immediately, in case field is pre-populated
    validateTextSearch(inputEl);
    // Then add an event listener to re-validate when input changes
    inputEl.addEventListener('input', function(event) {
      validateTextSearch(event.target);
    });
  }

  // Bootstrap the filter code's data persistence and
  // instantiate the controller that manages the UI components / views
  function init() {
    if (root.location.search === '') {
      root.location.search = '?status=new&status=open&no_status=false';
    }
    let filterUpdates = getQueryParams(root.location.search, Object.keys(initialFilterState));

    Object.keys(initialFilterState).forEach(function(key) {
      filterDataModel[key] = initialFilterState[key];
    });

    mutateFilterDataWithUpdates(filterDataModel, filterUpdates);

    filterController();
    initValidateTextSearch();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window, document);
