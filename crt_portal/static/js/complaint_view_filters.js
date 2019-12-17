(function(root, dom) {
  var SEARCH_PARAMS_WHITELIST = ['sort', 'page', 'per_page'];
  var FILTERS_WHITELIST = ['assigned_section'];
  var filterData = {
    assigned_section: []
  };

  /**
   * Convert an array-like object to an array.
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
   * Necessary because we can have multiple filters / search params
   * with the same name, and they all need to be passed in the final query
   */
  function getSearchParams(queryString) {
    var params = {};
    var search = new URLSearchParams(queryString);

    search.forEach(function(value, filterName) {
      if (SEARCH_PARAMS_WHITELIST.indexOf(filterName) >= 0) {
        params[filterName] = params[filterName] || [];

        if (params[filterName].indexOf(value) < 0) {
          params[filterName].push(encodeURIComponent(value));
        }
      }
    });

    return params;
  }

  function getFilterParams(queryString, dataStore) {
    var search = new URLSearchParams(queryString);

    search.forEach(function(value, filterName) {
      if (FILTERS_WHITELIST.indexOf(filterName) >= 0) {
        dataStore[filterName] = dataStore[filterName] || [];

        if (dataStore[filterName].indexOf(value) < 0) {
          dataStore[filterName].push(value);
        }
      }
    });
  }

  function getMutiselectValues(select) {
    var options = toArray((select && select.options) || []);

    return options
      .filter(function(option) {
        return option.selected;
      })
      .map(function(selected) {
        return selected.value;
      });
  }

  function makeQueryParam(key, value) {
    return key + '=' + encodeURIComponent(value);
  }

  function doSearch(form) {
    var paramsObj = getSearchParams(root.location.search);
    var filterKeys = Object.keys(filterData);
    var filters = filterKeys.reduce(function(memo, key) {
      var filter = filterData[key];

      if (filter instanceof Array) {
        filter.forEach(function(v) {
          memo.push(makeQueryParam(key, v));
        });
      } else {
        memo.push(makeQueryParam(key, filter));
      }

      return memo;
    }, []);

    var params = Object.keys(paramsObj).reduce(function(memo, paramName) {
      var values = paramsObj[paramName];

      var paramsString = values
        .reduce(function(accum, value) {
          accum.push(makeQueryParam(paramName, value));

          return accum;
        }, [])
        .join('&');

      memo.push(paramsString);

      return memo;
    }, []);

    var preparedFilters = filters.length ? '&' + filters.join('&') : '';
    var preparedParams = params.length ? params.join('&') : '';
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

  function filterController() {
    var form = dom.getElementById('filters-form');
    var activeFilters = dom.getElementById('active-filters');

    function onFilterTagClick(node) {
      var sections = filterData.assigned_section;
      var filterName = node.getAttribute('data-filter-value');

      sections.splice(sections.indexOf(filterName), 1);
      filterData.assigned_section = sections;

      doSearch(form);
    }

    getFilterParams(root.location.search, filterData);

    addFormSubmitBehavior({
      el: form
    });
    addMultiSelectBehavior({
      el: form.querySelector('select[name="assigned_section"')
    });
    addActiveFiltersBehavior({
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

  function addActiveFiltersBehavior(props) {
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
