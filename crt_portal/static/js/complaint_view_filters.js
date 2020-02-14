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
   * @param {Object} paramsObj An object containing initial
   * @returns {Array} A list of URI-encoded query param strings
   */
  function makeQueryParams(params) {
    var keys = Object.keys(params);

    return keys.reduce(function(memo, key) {
      var paramValue = params[key];
      var valueAsList = paramValue instanceof Array ? paramValue : [paramValue];

      if (!paramValue.length) {
        return memo;
      }

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

  /**
   * Concat all previous params together
   * @param {Array} params An array of URI-encoded query param strings
   * @returns {String} The supplies param strings joined and delimited by an ampersand
   */
  function finalizeQueryParams(params) {
    return params.length ? params.join('&') : '';
  }

  /**
   * filterDataModel and the mutation function below control the `model` behavior
   * of the filters JS
   */

  var filterDataModel = {
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
    location_city_town: '',
    create_date_start: '',
    create_date_end: '',
    sort: '',
    page: '',
    per_page: ''
  };

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

  /**
   * The following functions represent the 'views' for this  application —
   * these are the components that wire up event handling behavior to
   * specific DOM nodes.
   *
   * Each view takes a `props` object, which, at a minimum, accepts an `el` property, which is
   * an instance of the DOM node we want to add interactive behavior to.
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

  function getMutiselectValues(select) {
    var options = toArray((select && select.options) || []);

    function isSelected(option) {
      return option.selected;
    }

    function unwrapValue(x) {
      return x.value;
    }

    return options.filter(isSelected).map(unwrapValue);
  }
  /**
   * View to control multiselect elemeent behavior
   * @param {Object} props
   * @param {HTMLElement} props.el The DOM node this view manages
   */
  function multiSelectView(props) {
    props.el.addEventListener('change', function(event) {
      filterDataModel.assigned_section = getMutiselectValues(event.target);
    });
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

    props.el.addEventListener('change', function(event) {
      filterDataModel[props.name] = event.target.value;
    });
  }

  function filterController() {
    var formEl = dom.getElementById('filters-form');
    var multiSelectEl = formEl.querySelector('select[name="assigned_section"');
    var firstNameEl = formEl.querySelector('input[name="contact_first_name"');
    var lastNameEl = formEl.querySelector('input[name="contact_last_name"');
    var cityEl = formEl.querySelector('input[name="location_city_town"]');
    var locationStateEl = formEl.querySelector('select[name="location_state"]');
    var activeFiltersEl = dom.getElementById('active-filters');

    /**
     * Update the filter data model when the user clears (clicks on) a filter tag,
     * and perform a new search with the updated filters applied.
     * @param {HTMLElement} node An HTML element
     */
    function onFilterTagClick(node) {
      var filterName = node.getAttribute('data-filter-name');

      if (filterName === 'assigned_section') {
        var sections = filterDataModel.assigned_section;
        var filterData = node.getAttribute('data-filter-value');

        sections.splice(sections.indexOf(filterData), 1);
        filterDataModel.assigned_section = sections;
      } else {
        filterDataModel[filterName] = '';
      }

      formView.doSearch(formEl);
    }

    formView({
      el: formEl
    });
    multiSelectView({
      el: multiSelectEl
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
      el: cityEl,
      name: 'location_city_town'
    });
    textInputView({
      el: locationStateEl,
      name: 'location_state'
    });
    filterTagView({
      el: activeFiltersEl,
      onClick: onFilterTagClick
    });
  }

  // Bootstrap the filter code's data persistence and
  // instantiate the controller that manages the UI components / views
  function init() {
    var filterUpdates = getQueryParams(root.location.search, Object.keys(filterDataModel));
    mutateFilterDataWithUpdates(filterDataModel, filterUpdates);

    filterController();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window, document);
