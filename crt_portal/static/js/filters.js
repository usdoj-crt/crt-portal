(function(root, dom) {
  root.CRT = root.CRT || {};

  root.CRT.filterDataModel = {};

  function gtag() {
    window.dataLayer = window.dataLayer || [];
    dataLayer.push(arguments);
  }

  function sendGAFilterEvent(params) {
    const section = getSection();
    gtag('event', 'search_filter', { filters: params, section: section });
  }

  function getSection() {
    const sectionDropdown = document.getElementById('assigned-section-label');
    return sectionDropdown?.innerText;
  }
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
   * @param {String} queryString The query string we want to convert into an object
   * @param {Array} paramsAllowlist The list of accepted params
   * @returns {Object} Map of all params and their URL encoded values
   */
  root.CRT.getQueryParams = function(queryString, paramsAllowlist) {
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
  };

  /**
   * Given an object of query parameters, convert them back into a string
   * @param {Object} paramsObj The key/vslue pairs to be turned into query params
   * @returns {Array} A list of URI-encoded query param strings
   */
  function makeQueryParams(params) {
    const groupingEls = document.getElementsByName('grouping');
    const grouping = groupingEls.length ?? groupingEls[0].value;
    const persistentParams = ['group_params', 'page', 'per_page', 'sort', 'disposition_status'];
    var currentParams = root.CRT.getQueryParams(
      root.location.search,
      Object.keys(root.CRT.initialFilterState)
    );
    var keys = Object.keys(params);
    let resetGroupParams = false;
    const newParamKeys = [];
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
      if (valueToList[0] !== '') {
        var paramsString = valueToList
          .reduce(function(accum, value) {
            accum.push(makeQueryParam(key, value));
            newParamKeys.push(key);
            return accum;
          }, [])
          .join('&');

        memo.push(paramsString);
      }

      return memo;
    }, []);
    sendGAFilterEvent([newParamKeys].sort().join(' '));
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
   * Mutate the current filter state with updated filter values
   * @param {Object} state The current filter state
   * @param {Object} updates The properties of the filter state to be updated
   */
  root.CRT.mutateFilterDataWithUpdates = function(state, updates) {
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
        if (per_page_els.length === 1 && !state['group_params']?.length) {
          per_page_els[0].value = value;
        } else {
          state[key] = '';
          state['group_params'] = updateGroupParams(state['group_params'], per_page_els);
        }
      }
    }
  };

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
  root.CRT.filterTagView = function(props) {
    var filters = props.el;
    root.CRT.filterTagViewFilters = filters;
    var onClickHandler = props.onClick;

    filters.addEventListener('click', function handleFilterTagClick(event) {
      var node = event.target;
      if (node.tagName === 'BUTTON') {
        onClickHandler(node);
      }
    });
  };

  /**
   * View to control form element
   * @param {Object} props
   * @param {HTMLElement} props.el The DOM node this view manages
   */
  root.CRT.formView = function(props) {
    var form = props.el;

    form.addEventListener('submit', function handleSubmit(event) {
      event.preventDefault();

      root.CRT.formView.doSearch(form);
    });
  };

  /**
   * Create a query param string from our filter data model, and update the URL
   * in the browser to perform a new search with the applied filters
   */
  root.CRT.formView.doSearch = function(form) {
    var preparedFilters = finalizeQueryParams(makeQueryParams(root.CRT.filterDataModel));
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
  root.CRT.multiSelectView = function(props) {
    function onChange(event) {
      const newValue = root.CRT.buildMultiValue(
        event.target,
        root.CRT.multiSelectView.getValues(event.target)
      );
      root.CRT.filterDataModel[props.name] = newValue;
    }
    props.el.addEventListener('change', onChange);
    props.el.addEventListener('paste', dispatchChange);
  };

  root.CRT.selectRadio = function(radioButtonEls, filterName) {
    const valueToSet = root.CRT.filterDataModel[filterName];
    if (!valueToSet) return false;

    const buttonsToCheck = [...radioButtonEls].filter(el => valueToSet.includes(el.value));
    if (!buttonsToCheck.length) return false;

    buttonsToCheck.forEach(el => (el.checked = true));
    return true;
  };

  root.CRT.selectOption = function(selectEl, filterName) {
    const valueToSet = root.CRT.filterDataModel[filterName];
    if (!valueToSet) return false;

    const optionToSelect = [...selectEl.options].find(el => valueToSet.includes(el.value));
    if (!optionToSelect) return false;

    optionToSelect.selected = true;
    return true;
  };

  root.CRT.multiSelectView.getValues = function(select) {
    var options = toArray((select && select.options) || []);

    function isSelected(option) {
      return option.selected;
    }

    function unwrapValue(x) {
      return x.value;
    }

    return options.filter(isSelected).map(unwrapValue);
  };

  root.CRT.checkBoxView = function(props) {
    for (var i = 0; i < props.el.length; i++) {
      props.el[i].addEventListener('change', function(event) {
        root.CRT.buildMultiValue(event.target, root.CRT.checkBoxView.getValues(event.target));
      });
    }
  };

  root.CRT.radioButtonView = function(props) {
    props.el.forEach(el =>
      el.addEventListener('change', function(event) {
        if (event.target.checked) {
          root.CRT.filterDataModel[props.name] = event.target.value;
        }
      })
    );
  };

  root.CRT.submitView = function(props) {
    props.el.forEach(el => {
      el.addEventListener('click', function(event) {
        event.preventDefault();
        root.CRT.filterDataModel[props.name] = el.value;
        root.CRT.formView.doSearch(root.CRT.formEl);
      });
    });
  };

  root.CRT.checkBoxView.getValues = function(el) {
    if (el.checked) {
      root.CRT.filterDataModel[event.target.name].push(el.value);
    } else {
      var index = root.CRT.filterDataModel[event.target.name].indexOf(el.value);
      root.CRT.filterDataModel[event.target.name].splice(index, 1);
    }
  };

  /** Produces a new multi-field value given one of its constituent parts. */
  root.CRT.buildMultiValue = function(target, newValue) {
    const fieldName = target
      .getAttribute('id')
      ?.replace(/^id_/, '')
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
  };

  /**
   * View to control text input element behavior
   * @param {Object} props
   * @param {HTMLElement} props.el The DOM node this view manages
   * @param {String} props.name The key in the filter data model that corresponds to the data to update
   */
  root.CRT.textInputView = function(props) {
    if (!props.el || !props.name) {
      throw new Error(
        'Component must be supplied with a valid DOM node and a `name` key corresponding to a key in the filterDataModel object'
      );
    }
    function onChange(event) {
      const groupingEls = document.getElementsByName('grouping');
      const grouping = groupingEls.length ?? groupingEls[0].value;
      if (props.name == 'per_page' && grouping !== 'default') {
        const per_page_els = Array.from(document.getElementsByName('per_page'));
        root.CRT.filterDataModel['group_params'] = updateGroupParams(
          root.CRT.filterDataModel['group_params'],
          per_page_els
        );
      }
      if (props.name == 'per_page' || props.name == 'grouping') {
        root.CRT.filterDataModel[props.name] = event.target.value;
        dom.getElementById('apply-filters-button').click();
        return;
      }
      root.CRT.filterDataModel[props.name] = root.CRT.buildMultiValue(
        event.target,
        event.target.value
      );
    }
    props.el.addEventListener('change', onChange);
    props.el.addEventListener('paste', dispatchChange);
  };

  function updateGroupParams(group_params, per_page_els) {
    if (group_params?.length) {
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

  root.CRT.textInputsView = function(props) {
    props.el.forEach(el => {
      root.CRT.textInputView({
        el: el,
        name: props.name
      });
    });
  };

  root.CRT.clearFiltersView = function(props) {
    props.el.addEventListener('click', props.onClick);
  };

  root.CRT.onFilterTagClick = function(node) {
    var filterName = node.getAttribute('data-filter-name');

    const isMultiSelect = root.CRT.filterDataModel[filterName] instanceof Array;
    if (isMultiSelect) {
      var selections = root.CRT.filterDataModel[filterName];
      var selectionData = node.getAttribute('data-filter-value');
      selections.splice(selections.indexOf(selectionData), 1);
      root.CRT.filterDataModel[filterName] = selections;
    } else {
      root.CRT.filterDataModel[filterName] = '';
    }

    root.CRT.formView.doSearch(root.CRT.formEl);
  };

  root.CRT.clearAllFilters = function() {
    const activeFilters = toArray(root.CRT.filterTagViewFilters.children);

    var updates = activeFilters.reduce(function(updates, node) {
      var filterName = node.getAttribute('data-filter-name');
      var currentFilterData = root.CRT.filterDataModel[filterName];
      currentFilterData = wrapValue(currentFilterData);
      if (currentFilterData.length) {
        updates[filterName] = root.CRT.initialFilterState[filterName];
      }

      return updates;
    }, {});

    root.CRT.mutateFilterDataWithUpdates(root.CRT.filterDataModel, updates);
    root.CRT.formView.doSearch(root.CRT.formEl);
  };

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

  root.CRT.initValidateTextSearch = function() {
    var inputEl = document.getElementById('id_violation_summary');
    // Validate immediately, in case field is pre-populated
    validateTextSearch(inputEl);
    // Then add an event listener to re-validate when input changes
    inputEl.addEventListener('input', function(event) {
      validateTextSearch(event.target);
    });
  };

  root.CRT.applyArchivedCampaigns = function() {
    document.querySelectorAll('[data-archived="True"]').forEach(el => {
      const pair = document.querySelector(`[data-value="${el.value}"]`);
      if (!pair) return;
      pair.dataset.archived = true;
    });
  };

  root.CRT.applyCampaignSection = function() {
    document.querySelectorAll('[data-section]').forEach(el => {
      const pair = document.querySelector(`[data-value="${el.value}"]`);
      if (!pair) return;
      pair.dataset.section = el.dataset.section;
    });
  };

  root.CRT.observeCampaigns = function() {
    const observer = new MutationObserver((mutationList, observer) => {
      root.CRT.applyArchivedCampaigns();
      root.CRT.applyCampaignSection();
    });
    observer.observe(document.getElementById('id_origination_utm_campaign--list'), {
      childList: true
    });
  };
})(window, document);
