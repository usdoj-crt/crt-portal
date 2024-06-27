(function(root, dom) {
  root.CRT.initialFilterState = {
    sort: '',
    page: '',
    per_page: '',
    disposition_status: '',
    retention_schedule: '',
    expiration_date: '',
    status: Cookies.get('disposition_view_batch_status') || ''
  };

  function filterController() {
    root.CRT.formEl = dom.getElementById('sort-page-form');

    const perPageEl = dom.getElementsByName('per_page');
    const clearAllEl = dom.querySelector('[data-clear-filters]');
    const selectExpirationDateEl = dom.querySelector('select[name="expiration_date"]');
    const radioExpirationDateEls = dom.querySelectorAll('input[name="expiration_date"]');
    const retentionScheduleEls = dom.getElementsByName('retention_schedule');
    const dispositionStatusEls = dom.getElementsByName('disposition_status');
    const batchStatusEls = dom.getElementsByName('status');

    root.CRT.formView({
      el: root.CRT.formEl
    });

    root.CRT.textInputsView({
      el: perPageEl,
      name: 'per_page'
    });

    root.CRT.submitView({
      el: dispositionStatusEls,
      name: 'disposition_status'
    });

    if (selectExpirationDateEl) {
      root.CRT.textInputView({
        el: selectExpirationDateEl,
        name: 'expiration_date'
      });
      root.CRT.selectOption(selectExpirationDateEl, 'expiration_date');
    } else if (radioExpirationDateEls.length) {
      root.CRT.radioButtonView({
        el: radioExpirationDateEls,
        name: 'expiration_date'
      });
      root.CRT.selectRadio(radioExpirationDateEls, 'expiration_date');
    } else if (root.CRT.filterDataModel['expiration_date']) {
      const selectedExpirationLabel = dom.createElement('label');
      const ymd = root.CRT.filterDataModel['expiration_date'][0];
      const [year, month, day] = ymd.split('-');
      const mdy = `${month}/${day}/${year}`;
      selectedExpirationLabel.innerHTML = `
        ${mdy}
        <input type="radio" name="expiration_date" value="${ymd}" checked>
      `;
      dom.querySelector('.no-expiration').replaceWith(selectedExpirationLabel);
    }

    root.CRT.radioButtonView({
      el: retentionScheduleEls,
      name: 'retention_schedule'
    });
    root.CRT.selectRadio(retentionScheduleEls, 'retention_schedule');

    root.CRT.radioButtonView({
      el: batchStatusEls,
      name: 'status'
    });
    root.CRT.selectRadio(batchStatusEls, 'status');

    root.CRT.clearFiltersView({
      el: clearAllEl,
      onClick: () => {
        Cookies.remove('disposition_view_batch_status');
        const updates = {
          retention_schedule: '',
          expiration_date: '',
          status: ''
        };
        root.CRT.mutateFilterDataWithUpdates(root.CRT.filterDataModel, updates);
        root.CRT.formView.doSearch(root.CRT.formEl);
      }
    });
  }

  function init() {
    const search = new URLSearchParams(root.location.search);
    if (search.size === 0) {
      search.set('disposition_status', 'past');
    }
    if (!search.has('status') && root.CRT.initialFilterState['status']) {
      search.set('status', root.CRT.initialFilterState['status']);
    }

    root.history.replaceState({}, null, `?${search.toString()}`);

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
