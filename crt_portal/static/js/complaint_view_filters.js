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
    var paramsMap = {};
    var search = new URLSearchParams(queryString);
    var acceptedParams = (paramsWhitelist instanceof Array && paramsWhitelist) || [];

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
    const grouping = document.getElementsByName('grouping')[0].value;
    const persistentParams = ['group_params', 'page', 'per_page', 'sort'];
    var currentParams = getQueryParams(root.location.search, Object.keys(initialFilterState));
    var keys = Object.keys(params);
    let resetGroupParams = false;
    const newParams = keys.reduce(function(memo, key) {
      // Reset group params when grouping is set to default
      const paramValue = key === 'group_params' && grouping === 'default' ? [] : params[key];

      if (!paramValue || !paramValue.length) {
        // Reset group params when filter is removed
        if (!persistentParams.includes(key) && key in currentParams) {
          resetGroupParams = true;
        }
        return memo;
      }

      const currentParam = key in currentParams ? currentParams[key][0] : null;
      // Reset group params when new filter is added
      if (
        !persistentParams.includes(key) &&
        paramValue[0] != decodeFormData(currentParam) &&
        grouping != 'default'
      ) {
        resetGroupParams = true;
      }

      var valueToList = wrapValue(paramValue);
      var paramsString = valueToList
        .reduce(function(accum, value) {
          accum.push(makeQueryParam(key, value));

          return accum;
        }, [])
        .join('&');

      memo.push(paramsString);

      return memo;
    }, []);
    if (!resetGroupParams) return newParams;
    return newParams.filter(param => !param.includes('group_params'));
  }

  /**
   * Build a URI-encoded query paramater
   * @param {String} key The name of the query param
   * @param {String} value The value of the query param
   * @returns {String} Param in the format of {key}={value}
   */
  function makeQueryParam(key, value) {
    gtag('event', 'search_filter', { filter: key });
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

  var initialFilterState = {
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
    origination_utm_campaign: '',
    dj_number: '',
    public_id: '',
    primary_statute: '',
    district: '',
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
    contact_phone: '',
    correctional_facility_type: [],
    grouping: 'default',
    group_params: []
  };
  var filterDataModel = {};

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
      if (key === 'grouping') {
        document.getElementsByName('grouping')[0].value = value;
      }
      if (key === 'group_params' && state[key].length) {
        const per_page_els = document.getElementsByName('per_page');
        const group_params = JSON.parse(state[key][0].replaceAll('"', "'").replaceAll("'", '"'));
        per_page_els.forEach((el, i) => {
          el.value = group_params[i]['per_page'];
        });
      }
      if (key === 'per_page') {
        const per_page_els = Array.from(document.getElementsByName('per_page'));
        if (per_page_els.length === 1 && !state['group_params'].length) {
          per_page_els[0].value = value;
        } else {
          state[key] = '';
          state['group_params'] = updateGroupParams(state['group_params'], per_page_els);
        }
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
    var filters = props.el;
    var onClickHandler = props.onClick;

    filters.addEventListener('click', function handleFilterTagClick(event) {
      var node = event.target;
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
    var form = props.el;

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
    var preparedFilters = finalizeQueryParams(makeQueryParams(filterDataModel));
    var finalQuery = '';
    if (preparedFilters) {
      finalQuery = '?' + preparedFilters;
    }
    window.location = form.action + finalQuery;
  };

  function dispatchChange(event) {
    // setTimeout ensures the "change" event happens after the paste completes:
    setTimeout(() => {
      event.target.dispatchEvent(new Event('change'));
    }, 0);
  }

  /**
   * View to control multiselect element behavior
   * @param {Object} props
   * @param {HTMLElement} props.el The DOM node this view manages
   */
  function multiSelectView(props) {
    function onChange(event) {
      const newValue = buildMultiValue(event.target, multiSelectView.getValues(event.target));
      filterDataModel[props.name] = newValue;
    }
    props.el.addEventListener('change', onChange);
    props.el.addEventListener('paste', dispatchChange);
  }

  multiSelectView.getValues = function(select) {
    var options = toArray((select && select.options) || []);

    function isSelected(option) {
      return option.selected;
    }

    function unwrapValue(x) {
      return x.value;
    }

    return options.filter(isSelected).map(unwrapValue);
  };

  function checkBoxView(props) {
    for (var i = 0; i < props.el.length; i++) {
      props.el[i].addEventListener('change', function(event) {
        buildMultiValue(event.target, checkBoxView.getValues(event.target));
      });
    }
  }

  checkBoxView.getValues = function(el) {
    if (el.checked) {
      filterDataModel[event.target.name].push(el.value);
    } else {
      var index = filterDataModel[event.target.name].indexOf(el.value);
      filterDataModel[event.target.name].splice(index, 1);
    }
  };

  /** Produces a new multi-field value given one of its constituent parts. */
  function buildMultiValue(target, newValue) {
    const fieldName = target
      .getAttribute('id')
      .replace(/^id_/, '')
      .replace(/_[0-9]+$/, '');

    if (fieldName !== 'dj_number') return newValue;

    let subIndex = 0;
    let component;
    const changed = [];
    while ((component = document.querySelector(`#id_${fieldName}_${subIndex}`))) {
      changed.push(component.value || '');
      subIndex++;
    }

    return changed.join('-');
  }

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
    function onChange(event) {
      const grouping = document.getElementsByName('grouping')[0].value;
      if (props.name == 'per_page' && grouping !== 'default') {
        const per_page_els = Array.from(document.getElementsByName('per_page'));
        filterDataModel['group_params'] = updateGroupParams(
          filterDataModel['group_params'],
          per_page_els
        );
      }
      if (props.name == 'per_page' || props.name == 'grouping') {
        filterDataModel[props.name] = event.target.value;
        dom.getElementById('apply-filters-button').click();
        return;
      }
      filterDataModel[props.name] = buildMultiValue(event.target, event.target.value);
    }
    props.el.addEventListener('change', onChange);
    props.el.addEventListener('paste', dispatchChange);
  }

  function updateGroupParams(group_params, per_page_els) {
    if (group_params.length) {
      group_params = JSON.parse(group_params[0]?.replaceAll('"', "'").replaceAll("'", '"'));
      per_page_els.forEach((el, i) => {
        group_params[i]['per_page'] = el.value ? Number(el.value) : 15;
      });
      return JSON.stringify(group_params);
    }
    return JSON.stringify(
      per_page_els.map(el => {
        return {
          page: 1,
          per_page: el.value ? Number(el.value) : 15,
          sort: []
        };
      })
    );
  }

  function textInputsView(props) {
    props.el.forEach(el => {
      textInputView({
        el: el,
        name: props.name
      });
    });
  }

  function clearFiltersView(props) {
    props.el.addEventListener('click', props.onClick);
  }

  function filterController() {
    var formEl = dom.getElementById('filters-form');
    var firstNameEl = formEl.querySelector('input[name="contact_first_name"]');
    var lastNameEl = formEl.querySelector('input[name="contact_last_name"]');
    var locationCityEl = formEl.querySelector('input[name="location_city_town"]');
    var locationNameEl = formEl.querySelector('input[name="location_name"]');
    var locationStateEl = dom.getElementsByName('location_state');
    var activeFiltersEl = dom.querySelector('[data-active-filters]');
    var clearAllEl = dom.querySelector('[data-clear-filters]');
    var statusEl = dom.getElementsByName('status');
    var summaryEl = formEl.querySelector('input[name="summary"]');
    var createdatestartEl = formEl.querySelector('input[name="create_date_start"]');
    var createdateendEl = formEl.querySelector('input[name="create_date_end"]');
    var assigneeEl = formEl.querySelector('#id_assigned_to');
    var campaignEl = formEl.querySelector('#id_origination_utm_campaign');
    var djNumberEl = formEl.querySelectorAll('.crt-dj-number input');
    var complaintIDEl = formEl.querySelector('input[name="public_id"]');
    var statuteEl = formEl.querySelector('select[name="primary_statute"]');
    var districtEl = formEl.querySelector('select[name="district"]');
    var perPageEl = dom.getElementsByName('per_page');
    var groupingEl = dom.querySelector('select[name="grouping"]');
    var personalDescriptionEl = formEl.querySelector('textarea[name="violation_summary"]');
    var primaryIssueEl = dom.getElementsByName('primary_complaint');
    var reportedReasonEl = dom.getElementsByName('reported_reason');
    var relevantDetailsEl = dom.getElementsByName('commercial_or_public_place');
    var intakeFormatEl = dom.getElementsByName('intake_format');
    var hateCrimeEl = dom.getElementsByName('hate_crime');
    var servicememberEl = dom.getElementsByName('servicemember');
    var contactEmailEl = dom.querySelector('input[name="contact_email"]');
    var referredEl = dom.getElementsByName('referred');
    var languageEl = dom.getElementsByName('language');
    var contactPhoneEL = dom.getElementsByName('contact_phone')[0];
    var correctionalFacilityTypeEl = dom.getElementsByName('correctional_facility_type');
    /**
     * Update the filter data model when the user clears (clicks on) a filter tag,
     * and perform a new search with the updated filters applied.
     * @param {HTMLElement} node An HTML element
     */
    function onFilterTagClick(node) {
      var filterName = node.getAttribute('data-filter-name');

      // see if we have to process multiple select elements first
      var multiSelectElements = [
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
      var filterIndex = multiSelectElements.indexOf(filterName);
      if (filterIndex !== -1) {
        var selections = filterDataModel[filterName];
        var selectionData = node.getAttribute('data-filter-value');
        selections.splice(selections.indexOf(selectionData), 1);
        filterDataModel[filterName] = selections;
      } else {
        filterDataModel[filterName] = '';
      }

      formView.doSearch(formEl);
    }

    function clearAllFilters() {
      const activeFilters = toArray(activeFiltersEl.children);

      var updates = activeFilters.reduce(function(updates, node) {
        var filterName = node.getAttribute('data-filter-name');
        var currentFilterData = filterDataModel[filterName];
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
      el: campaignEl,
      name: 'origination_utm_campaign'
    });
    textInputView({
      el: personalDescriptionEl,
      name: 'violation_summary'
    });
    textInputView({
      el: createdatestartEl,
      name: 'create_date_start'
    });
    textInputView({
      el: createdateendEl,
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
      el: districtEl,
      name: 'district'
    });
    textInputsView({
      el: perPageEl,
      name: 'per_page'
    });
    textInputsView({
      el: djNumberEl,
      name: 'dj_number'
    });
    textInputView({
      el: groupingEl,
      name: 'grouping'
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
    textInputView({
      el: contactPhoneEL,
      name: 'contact_phone'
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
    var buttonEl = document.getElementById('apply-filters-button');
    var alertEl = document.getElementById('search-notification');
    var textEl = alertEl.querySelector('.usa-alert__text');
    var value = el.value;
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
    var inputEl = document.getElementById('id_violation_summary');
    // Validate immediately, in case field is pre-populated
    validateTextSearch(inputEl);
    // Then add an event listener to re-validate when input changes
    inputEl.addEventListener('input', function(event) {
      validateTextSearch(event.target);
    });
  }

  function applyArchivedCampaigns() {
    document.querySelectorAll('[data-archived="True"]').forEach(el => {
      const pair = document.querySelector(`[data-value="${el.value}"]`);
      if (!pair) return;
      pair.dataset.archived = true;
    });
  }

  function applyCampaignSection() {
    document.querySelectorAll('[data-section]').forEach(el => {
      const pair = document.querySelector(`[data-value="${el.value}"]`);
      if (!pair) return;
      pair.dataset.section = el.dataset.section;
    });
  }

  function observeCampaigns() {
    const observer = new MutationObserver((mutationList, observer) => {
      applyArchivedCampaigns();
      applyCampaignSection();
    });
    observer.observe(document.getElementById('id_origination_utm_campaign--list'), {
      childList: true
    });
  }

  // Bootstrap the filter code's data persistence and
  // instantiate the controller that manages the UI components / views
  function init() {
    if (root.location.search === '') {
      root.location.search = '?status=new&status=open&no_status=false&grouping=default';
    }
    var filterUpdates = getQueryParams(root.location.search, Object.keys(initialFilterState));

    Object.keys(initialFilterState).forEach(function(key) {
      filterDataModel[key] = initialFilterState[key];
    });

    mutateFilterDataWithUpdates(filterDataModel, filterUpdates);

    filterController();
    initValidateTextSearch();
    applyArchivedCampaigns();
    observeCampaigns();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window, document);
