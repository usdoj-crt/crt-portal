(function(root, dom) {
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

  function getSection() {
    const sectionDropdown = document.getElementById('assigned-section-label');
    return sectionDropdown?.innerText;
  }

  function gtag() {
    window.dataLayer = window.dataLayer || [];
    dataLayer.push(arguments);
  }

  function sendGAFilterEvent(params) {
    const section = getSection();
    gtag('event', 'search_filter', { filters: params, section: section });
  }

  /**
   * Given an object of query parameters, convert them back into a string
   * @param {Object} paramsObj The key/vslue pairs to be turned into query params
   * @returns {Array} A list of URI-encoded query param strings
   */
  function makeQueryParams(params) {
    var keys = Object.keys(params);
    const newParamKeys = [];
    const newParams = keys.reduce(function(memo, key) {
      const paramValue = params[key];
      if (!paramValue || !paramValue.length) {
        return memo;
      }

      var valueToList = wrapValue(paramValue);
      var paramsString = valueToList
        .reduce(function(accum, value) {
          accum.push(makeQueryParam(key, value));
          newParamKeys.push(key);
          return accum;
        }, [])
        .join('&');

      memo.push(paramsString);

      return memo;
    }, []);
    sendGAFilterEvent([newParamKeys].sort().join(' '));
    return newParams;
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
    sort: '',
    page: '',
    per_page: '',
    disposition_status: ''
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
        const per_page_els = Array.from(document.getElementsByName('per_page'));
        if (per_page_els.length === 1) {
          per_page_els[0].value = value;
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
      dom.getElementById('apply-filters-button').click();
      return;
    }
    props.el.addEventListener('change', onChange);
  }

  function textInputsView(props) {
    props.el.forEach(el => {
      textInputView({
        el: el,
        name: props.name
      });
    });
  }

  function filterController() {
    var formEl = dom.getElementById('filters-form');
    var perPageEl = dom.getElementsByName('per_page');

    formView({
      el: formEl
    });
    textInputsView({
      el: perPageEl,
      name: 'per_page'
    });
  }

  // Bootstrap the filter code's data persistence and
  // instantiate the controller that manages the UI components / views
  function init() {
    if (root.location.search === '') {
      root.location.search = '?disposition_status=past';
    }
    var filterUpdates = getQueryParams(root.location.search, Object.keys(initialFilterState));

    Object.keys(initialFilterState).forEach(function(key) {
      filterDataModel[key] = initialFilterState[key];
    });

    mutateFilterDataWithUpdates(filterDataModel, filterUpdates);

    filterController();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window, document);
