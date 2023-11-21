(function(root, dom) {
  root.CRT.initialFilterState = {
    create_date_start: '',
    create_date_end: '',
    assigned_to: '',
    actions: [],
    sort: '',
    page: '',
    per_page: '',
    public_id: ''
  };

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
    root.CRT.formEl = dom.getElementById('filters-form');
    var activeFiltersEl = dom.querySelector('[data-active-filters]');
    var createdatestartEl = root.CRT.formEl.querySelector('input[name="create_date_start"]');
    var createdateendEl = root.CRT.formEl.querySelector('input[name="create_date_end"]');
    var clearAllEl = dom.querySelector('[data-clear-filters]');
    var assigneeEl = root.CRT.formEl.querySelector('#id_assigned_to');
    const actionsEl = dom.getElementsByName('actions');
    const complaintIDEl = root.CRT.formEl.querySelector('input[name="public_id"]');
    const perPageEl = dom.querySelector('select[name="per_page"]');

    root.CRT.formView({
      el: root.CRT.formEl
    });
    root.CRT.filterTagView({
      el: activeFiltersEl,
      onClick: root.CRT.onFilterTagClick
    });
    root.CRT.textInputView({
      el: assigneeEl,
      name: 'assigned_to'
    });
    root.CRT.textInputView({
      el: createdatestartEl,
      name: 'create_date_start'
    });
    root.CRT.textInputView({
      el: createdateendEl,
      name: 'create_date_end'
    });
    const location = window.location.href;
    if (location.includes('activity')) {
      root.CRT.checkBoxView({
        el: actionsEl,
        name: 'actions'
      });
      root.CRT.textInputView({
        el: perPageEl,
        name: 'per_page'
      });
      root.CRT.textInputView({
        el: complaintIDEl,
        name: 'public_id'
      });
    }
    root.CRT.clearFiltersView({
      el: clearAllEl,
      onClick: root.CRT.clearAllFilters
    });
  }

  // Bootstrap the filter code's data persistence and
  // instantiate the controller that manages the UI components / views
  function init() {
    var filterUpdates = root.CRT.getQueryParams(
      root.location.search,
      Object.keys(root.CRT.initialFilterState)
    );

    Object.keys(root.CRT.initialFilterState).forEach(function(key) {
      root.CRT.filterDataModel[key] = root.CRT.initialFilterState[key];
    });
    const buttonEl = document.getElementById('apply-filters-button');
    buttonEl.addEventListener('click', function(e) {
      validateFilter(e);
    });
    root.CRT.mutateFilterDataWithUpdates(root.CRT.filterDataModel, filterUpdates);

    filterController();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window, document);
