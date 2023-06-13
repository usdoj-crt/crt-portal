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
    var keys = Object.keys(params);
    return keys.reduce(function(memo, key) {
      var paramValue = params[key];

      if (!paramValue || !paramValue.length) {
        return memo;
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

  var initialFilterState = {
    create_date_start: '',
    create_date_end: '',
    assigned_to: '',
    actions: [],
    sort: '',
    page: '',
    per_page: '',
    public_id: ''
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
      if (key === 'per_page') {
        const per_page_el = dom.querySelector('select[name="per_page"]');
        if (per_page_el) {
          per_page_el.value = value;
        } else {
          state[key] = '';
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
        checkBoxView.getValues(event.target);
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
      filterDataModel[props.name] = event.target.value;
      if (props.name == 'per_page') {
        dom.getElementById('apply-filters-button').click();
        return;
      }
    }
    props.el.addEventListener('change', onChange);
  }

  function clearFiltersView(props) {
    props.el.addEventListener('click', props.onClick);
  }

  function validateFilter(e) {
    const buttonEl = document.getElementById('apply-filters-button');
    const inputEl = document.getElementById('id_assigned_to');
    const alertEl = document.getElementById('filter-notification');
    if (!alertEl) return;
    const textEl = alertEl.querySelector('.usa-alert__text');
    const value = inputEl.value;
    if (!value.length || value == '(none)') {
      e.preventDefault();
      buttonEl.setAttribute('disabled', '');
      textEl.textContent = 'Please select an intake specialist to see activity log data';
      alertEl.style.display = 'inline-block';
      inputEl.addEventListener('change', e => {
        validateFilter(e);
      });
    } else {
      buttonEl.removeAttribute('disabled');
      textEl.textContent = '';
      alertEl.style.display = 'none';
    }
  }

  function filterController() {
    var formEl = dom.getElementById('filters-form');
    var activeFiltersEl = dom.querySelector('[data-active-filters]');
    var createdatestartEl = formEl.querySelector('input[name="create_date_start"]');
    var createdateendEl = formEl.querySelector('input[name="create_date_end"]');
    var clearAllEl = dom.querySelector('[data-clear-filters]');
    var assigneeEl = formEl.querySelector('#id_assigned_to');
    const actionsEl = dom.getElementsByName('actions');
    const complaintIDEl = formEl.querySelector('input[name="public_id"]');
    const perPageEl = dom.querySelector('select[name="per_page"]');
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
        'correctional_facility_type',
        'actions'
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
    filterTagView({
      el: activeFiltersEl,
      onClick: onFilterTagClick
    });
    textInputView({
      el: assigneeEl,
      name: 'assigned_to'
    });
    textInputView({
      el: createdatestartEl,
      name: 'create_date_start'
    });
    textInputView({
      el: createdateendEl,
      name: 'create_date_end'
    });
    const location = window.location.href;
    if (location.includes('activity')) {
      checkBoxView({
        el: actionsEl,
        name: 'actions'
      });
      textInputView({
        el: perPageEl,
        name: 'per_page'
      });
      textInputView({
        el: complaintIDEl,
        name: 'public_id'
      });
    }
    clearFiltersView({
      el: clearAllEl,
      onClick: clearAllFilters
    });
  }

  // Bootstrap the filter code's data persistence and
  // instantiate the controller that manages the UI components / views
  function init() {
    var filterUpdates = getQueryParams(root.location.search, Object.keys(initialFilterState));

    Object.keys(initialFilterState).forEach(function(key) {
      filterDataModel[key] = initialFilterState[key];
    });
    const buttonEl = document.getElementById('apply-filters-button');
    buttonEl.addEventListener('click', function(e) {
      validateFilter(e);
    });
    mutateFilterDataWithUpdates(filterDataModel, filterUpdates);

    filterController();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window, document);
