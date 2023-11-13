(function(root, dom) {
  // 'Box' an element in an array if it isn't one currently
  function wrapValue(maybeUnboxed) {
    return Array.isArray(maybeUnboxed) ? maybeUnboxed : [maybeUnboxed];
  }

  /**
   * @param {String} queryString The query string we want to convert into an object
   * @param {Array} paramsAllowlist The list of accepted params
   * @returns {Object} Map of all params and their URL encoded values
   */
  function getQueryParams(queryString, paramsAllowlist) {
    const paramsMap = {};
    const search = new URLSearchParams(queryString);
    const acceptedParams = (paramsAllowlist instanceof Array && paramsAllowlist) || [];

    search.forEach(function(value, name) {
      if (acceptedParams.indexOf(name) >= 0) {
        paramsMap[name] = paramsMap[name] || [];

        if (paramsMap[name].indexOf(value) < 0) {
          paramsMap[name].push(encodeURIComponent(value));
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
    const keys = Object.keys(params);
    const newParamKeys = [];
    const newParams = keys.reduce(function(memo, key) {
      const paramValue = params[key];
      if (!paramValue || !paramValue.length) {
        return memo;
      }

      const valueToList = wrapValue(paramValue);
      const paramsString = valueToList
        .reduce(function(accum, value) {
          accum.push(makeQueryParam(key, value));
          newParamKeys.push(key);
          return accum;
        }, [])
        .join('&');

      memo.push(paramsString);

      return memo;
    }, []);
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
   * dataModel and the mutation function below control the `model` behavior
   * of the query
   */

  const initialState = {
    sort: '',
    page: '',
    per_page: '',
    disposition_status: ''
  };
  const dataModel = {};

  /**
   * Mutate the current state with updated values
   * @param {Object} state The current state
   * @param {Object} updates The properties of the state to be updated
   */
  function mutateDataWithUpdates(state, updates) {
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
    const form = props.el;

    form.addEventListener('submit', function handleSubmit(event) {
      event.preventDefault();

      formView.doSearch(form);
    });
  }

  /**
   * Create a query param string from the data model, and update the URL
   * in the browser to perform a new search with the applied query
   */
  formView.doSearch = function doSearch(form) {
    const preparedData = finalizeQueryParams(makeQueryParams(dataModel));
    let finalQuery = '';
    if (preparedData) {
      finalQuery = '?' + preparedData;
    }
    window.location = form.action + finalQuery;
  };

  /**
   * View to control text input element behavior
   * @param {Object} props
   * @param {HTMLElement} props.el The DOM node this view manages
   * @param {String} props.name The key in the data model that corresponds to the data to update
   */
  function textInputView(props) {
    if (!props.el || !props.name) {
      throw new Error(
        'Component must be supplied with a valid DOM node and a `name` key corresponding to a key in the dataModel object'
      );
    }
    function onChange(event) {
      dataModel[props.name] = event.target.value;
      dom.getElementById('apply-sort-page-button').click();
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

  function dataController() {
    const formEl = dom.getElementById('sort-page-form');
    const perPageEl = dom.getElementsByName('per_page');

    formView({
      el: formEl
    });
    textInputsView({
      el: perPageEl,
      name: 'per_page'
    });
  }


  function init() {
    if (root.location.search === '') {
      root.location.search = '?disposition_status=past';
    }
    const updates = getQueryParams(root.location.search, Object.keys(initialState));

    Object.keys(initialState).forEach(function(key) {
      dataModel[key] = initialState[key];
    });

    mutateDataWithUpdates(dataModel, updates);

    dataController();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window, document);
