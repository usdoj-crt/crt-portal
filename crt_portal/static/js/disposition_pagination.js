(function(root, dom) {
  root.CRT.initialFilterState = {
    sort: '',
    page: '',
    per_page: '',
    disposition_status: ''
  };

  function filterController() {
    root.CRT.formEl = dom.getElementById('sort-page-form');
    const perPageEl = dom.getElementsByName('per_page');

    root.CRT.formView({
      el: root.CRT.formEl
    });
    root.CRT.textInputsView({
      el: perPageEl,
      name: 'per_page'
    });
  }

  function init() {
    if (root.location.search === '') {
      root.location.search = '?disposition_status=past';
    }
    const updates = root.CRT.getQueryParams(
      root.location.search,
      Object.keys(root.CRT.initialFilterState)
    );

    Object.keys(root.CRT.initialFilterState).forEach(function(key) {
      root.CRT.filterDataModel[key] = root.CRT.initialFilterState[key];
    });

    root.CRT.mutateFilterDataWithUpdates(root.CRT.filterDataModel, updates);

    filterController();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window, document);
