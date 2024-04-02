(function(root, dom) {
  root.CRT.initialFilterState = {
    sort: '',
    page: '',
    per_page: '',
    saved_search_view: '',
    section_filter: []
  };

  function filterController() {
    root.CRT.formEl = dom.getElementById('filters-form');
    const perPageEl = dom.getElementsByName('per_page');
    const sectionEl = dom.getElementsByName('section_filter');
    root.CRT.formView({
      el: root.CRT.formEl
    });
    root.CRT.textInputsView({
      el: perPageEl,
      name: 'per_page'
    });
    root.CRT.checkBoxView({
      el: sectionEl,
      name: 'section_filter'
    });
  }

  function init() {
    if (root.location.search === '') {
      root.location.search = '?saved_search_view=all';
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
