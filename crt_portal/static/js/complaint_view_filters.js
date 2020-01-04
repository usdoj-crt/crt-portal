(function(root, dom) {
  var SEARCH_PARAMS_WHITELIST = ['sort', 'page', 'per_page'];
  var filterData = {
    assigned_section: [],
    primary_complaint: '',
    status: '',
    location_state: '',
    primary_complaint: '',
    contact_first_name: '',
    contact_last_name: '',
    contact_email: '',
    other_class: '',
    violation_summary: '',
    location_name: '',
    location_address_line_1: '',
    location_address_line_2: '',
    create_date_start: '',
    create_date_end: '',
  };

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
   * Mutate the current filter state with updated filter values
   * @param {Object} state The current filter state
   * @param {Object} updates The properties of the filter state to be updated
   */
  function mutateFilterDataWithUpdates(state, updates) {
    for (var key in updates) {
      if (state.hasOwnProperty(key)) {
        state[key] = updates[key];
      }
    }
  }

  function getMutiselectValues(select) {
    var options = toArray((select && select.options) || []);

    function isSelected(option) {
      return option.selected;
    }

    function unwrapValue(x) {
      return x.value;
    }

    return options
      .filter(isSelected)
      .map(unwrapValue);
  }

  /**
   * Given an object of query parameters, convert them back into a string
   * @param {Object} paramsObj An object containing initial
   * @returns {Array} A list of URI-encoded query param strings
   */
  function makeQueryParams(params) {
    var keys = Object.keys(params);

    return keys.reduce(function(memo, key) {
      var paramValue = params[key];

      if (!paramValue) {
        return memo;
      }

      var valueAsList = paramValue instanceof Array ? paramValue : [ paramValue ];
      var paramsString = valueAsList
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

  function finalizeQueryParams(params) {
    return params.length ? params.join('&') : '';
  }

  function doSearch(form) {
    var paramsObj = getQueryParams(root.location.search, SEARCH_PARAMS_WHITELIST);
    var preparedFilters = finalizeQueryParams(makeQueryParams(filterData));
    var preparedParams = finalizeQueryParams(makeQueryParams(paramsObj));
    var finalQuery = '';

    if (preparedFilters || preparedParams) {
      finalQuery = '?' + preparedParams + preparedFilters;
    }

    window.location = form.action + finalQuery;
  }

  function addMultiSelectBehavior(props) {
    props.el.addEventListener('change', function(event) {
      filterData.assigned_section = getMutiselectValues(event.target);
    });
  }

  function addTextInputBehavior(props) {
    if (!props.el || !props.name) {
      throw new Error(
        'Component must be supplied with a valid DOM node and a `name` key corresponding to a key in the filterData object'
      );
    }

    props.el.addEventListener('change', function(event) {
      filterData[props.name] = event.target.value;
    });
  }

  function filterController() {
    var form = dom.getElementById('filters-form');
    var activeFilters = dom.getElementById('active-filters');

    function onFilterTagClick(node) {
      var sections = filterData.assigned_section;
      var filterName = node.getAttribute('data-filter-name');

      if (filterName === 'assigned_section') {
        sections.splice(sections.indexOf(filterName), 1);
        filterData.assigned_section = sections;
      } else {
        filterData[filterName] = '';
      }

      doSearch(form);
    }

    var filterUpdates = getQueryParams(root.location.search, Object.keys(filterData));
    mutateFilterDataWithUpdates(filterData, filterUpdates);

    addFormSubmitBehavior({
      el: form
    });
    addMultiSelectBehavior({
      el: form.querySelector('select[name="assigned_section"')
    });
    addTextInputBehavior({
      el: form.querySelector('input[name="contact_first_name"'),
      name: 'contact_first_name'
    });
    addTextInputBehavior({
      el: form.querySelector('input[name="contact_last_name"'),
      name: 'contact_last_name'
    });
    addFilterTagBehavior({
      el: activeFilters,
      onClick: onFilterTagClick
    });
  }

  function addFormSubmitBehavior(props) {
    var form = props.el;

    form.addEventListener('submit', function handleSubmit(event) {
      event.preventDefault();

      doSearch(form);
    });
  }

  function addFilterTagBehavior(props) {
    var filters = props.el;
    var onClickHandler = props.onClick;

    filters.addEventListener('click', function handleFilterTagClick(event) {
      var node = event.target;

      if (node.tagName === 'BUTTON') {
        onClickHandler(node);
      }
    });
  }

  window.addEventListener('DOMContentLoaded', filterController);
})(window, document);
