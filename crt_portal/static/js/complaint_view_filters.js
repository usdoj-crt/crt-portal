(function(root, dom) {
  /**
   * filterDataModel and the mutation function below control the `model` behavior
   * of the filters
   */

  root.CRT.initialFilterState = {
    status: [],
    location_state: [],
    primary_complaint: [],
    contact_first_name: '',
    contact_last_name: '',
    contact_email: '',
    violation_summary: [],
    location_name: '',
    location_name_1: '0',
    location_name_2: '0',
    location_address_line_1: '',
    location_address_line_2: '',
    location_city_town: '',
    create_date_start: '',
    create_date_end: '',
    summary: '',
    assigned_to: '',
    origination_utm_campaign: '',
    dj_number: '',
    tags: [],
    public_id: '',
    primary_statute: '',
    district: '',
    reported_reason: [],
    commercial_or_public_place: [],
    intake_format: [],
    servicemember: [],
    hate_crime: [],
    referred: [],
    sort: '',
    page: '',
    per_page: '',
    no_status: '',
    language: [],
    contact_phone: '',
    correctional_facility_type: [],
    grouping: 'default',
    group_params: [],
    litigation_hold: [],
    retention_schedule: []
  };

  function filterController() {
    root.CRT.formEl = dom.getElementById('filters-form');
    const firstNameEl = root.CRT.formEl.querySelector('input[name="contact_first_name"]');
    const lastNameEl = root.CRT.formEl.querySelector('input[name="contact_last_name"]');
    const locationCityEl = root.CRT.formEl.querySelector('input[name="location_city_town"]');
    const locationNameEl = root.CRT.formEl.querySelector('input[name="location_name"]');
    const locationName1El = root.CRT.formEl.querySelector('input[name="location_name_1"]');
    const locationName2El = root.CRT.formEl.querySelector('input[name="location_name_2"]');
    const locationStateEl = dom.getElementsByName('location_state');
    const activeFiltersEl = dom.querySelector('[data-active-filters]');
    const clearAllEl = dom.querySelector('[data-clear-filters]');
    const statusEl = dom.getElementsByName('status');
    const summaryEl = root.CRT.formEl.querySelector('input[name="summary"]');
    const createdatestartEl = root.CRT.formEl.querySelector('input[name="create_date_start"]');
    const createdateendEl = root.CRT.formEl.querySelector('input[name="create_date_end"]');
    const assigneeEl = root.CRT.formEl.querySelector('#id_assigned_to');
    const campaignEl = root.CRT.formEl.querySelector('#id_origination_utm_campaign');
    const djNumberEl = root.CRT.formEl.querySelectorAll('.crt-dj-number input');
    const complaintIDEl = root.CRT.formEl.querySelector('input[name="public_id"]');
    const statuteEl = root.CRT.formEl.querySelector('select[name="primary_statute"]');
    const districtEl = root.CRT.formEl.querySelector('select[name="district"]');
    const perPageEl = dom.getElementsByName('per_page');
    const groupingEl = dom.querySelector('select[name="grouping"]');
    const personalDescriptionEl = root.CRT.formEl.querySelector(
      'textarea[name="violation_summary"]'
    );
    const primaryIssueEl = dom.getElementsByName('primary_complaint');
    const tagsEl = dom.getElementsByName('tags');
    const reportedReasonEl = dom.getElementsByName('reported_reason');
    const relevantDetailsEl = dom.getElementsByName('commercial_or_public_place');
    const intakeFormatEl = dom.getElementsByName('intake_format');
    const hateCrimeEl = dom.getElementsByName('hate_crime');
    const servicememberEl = dom.getElementsByName('servicemember');
    const contactEmailEl = dom.querySelector('input[name="contact_email"]');
    const referredEl = dom.getElementsByName('referred');
    const languageEl = dom.getElementsByName('language');
    const contactPhoneEL = dom.getElementsByName('contact_phone')[0];
    const correctionalFacilityTypeEl = dom.getElementsByName('correctional_facility_type');
    const litigationHoldEl = dom.getElementsByName('litigation_hold');
    const retentionScheduleEl = dom.getElementsByName('retention_schedule');

    root.CRT.formView({
      el: root.CRT.formEl
    });
    root.CRT.textInputView({
      el: firstNameEl,
      name: 'contact_first_name'
    });
    root.CRT.textInputView({
      el: lastNameEl,
      name: 'contact_last_name'
    });
    root.CRT.textInputView({
      el: locationCityEl,
      name: 'location_city_town'
    });
    root.CRT.textInputView({
      el: locationNameEl,
      name: 'location_name'
    });
    root.CRT.textInputView({
      el: locationName1El,
      name: 'location_name_1'
    });
    root.CRT.textInputView({
      el: locationName2El,
      name: 'location_name_2'
    });
    root.CRT.checkBoxView({
      el: locationStateEl,
      name: 'location_state'
    });
    root.CRT.filterTagView({
      el: activeFiltersEl,
      onClick: root.CRT.onFilterTagClick
    });
    root.CRT.checkBoxView({
      el: statusEl,
      name: 'status'
    });
    root.CRT.textInputView({
      el: summaryEl,
      name: 'summary'
    });
    root.CRT.textInputView({
      el: assigneeEl,
      name: 'assigned_to'
    });
    root.CRT.textInputView({
      el: campaignEl,
      name: 'origination_utm_campaign'
    });
    root.CRT.textInputView({
      el: personalDescriptionEl,
      name: 'violation_summary'
    });
    root.CRT.textInputView({
      el: createdatestartEl,
      name: 'create_date_start'
    });
    root.CRT.textInputView({
      el: createdateendEl,
      name: 'create_date_end'
    });
    root.CRT.textInputView({
      el: complaintIDEl,
      name: 'public_id'
    });
    root.CRT.textInputView({
      el: statuteEl,
      name: 'primary_statute'
    });
    root.CRT.textInputView({
      el: districtEl,
      name: 'district'
    });
    root.CRT.textInputsView({
      el: perPageEl,
      name: 'per_page'
    });
    root.CRT.textInputsView({
      el: djNumberEl,
      name: 'dj_number'
    });
    root.CRT.textInputView({
      el: groupingEl,
      name: 'grouping'
    });
    root.CRT.clearFiltersView({
      el: clearAllEl,
      onClick: root.CRT.clearAllFilters
    });
    root.CRT.checkBoxView({
      el: primaryIssueEl,
      name: 'primary_complaint'
    });
    root.CRT.checkBoxView({
      el: tagsEl,
      name: 'tags'
    });
    root.CRT.checkBoxView({
      el: reportedReasonEl,
      name: 'reported_reason'
    });
    root.CRT.checkBoxView({
      el: relevantDetailsEl,
      name: 'commercial_or_public_place'
    });
    root.CRT.checkBoxView({
      el: intakeFormatEl,
      name: 'intake_format'
    });
    root.CRT.checkBoxView({
      el: hateCrimeEl,
      name: 'hate_crime'
    });
    root.CRT.checkBoxView({
      el: servicememberEl,
      name: 'servicemember'
    });
    root.CRT.textInputView({
      el: contactEmailEl,
      name: 'contact_email'
    });
    root.CRT.textInputView({
      el: contactPhoneEL,
      name: 'contact_phone'
    });
    root.CRT.checkBoxView({
      el: referredEl,
      name: 'referred'
    });
    root.CRT.checkBoxView({
      el: languageEl,
      name: 'language'
    });
    root.CRT.checkBoxView({
      el: correctionalFacilityTypeEl,
      name: 'correctional_facility_type'
    });
    root.CRT.checkBoxView({
      el: litigationHoldEl,
      name: 'litigation_hold'
    });
    root.CRT.checkBoxView({
      el: retentionScheduleEl,
      name: 'retention_schedule'
    });
  }
  // Bootstrap the filter code's data persistence and
  // instantiate the controller that manages the UI components / views
  function init() {
    if (root.location.search === '') {
      root.location.search = '?status=new&status=open&no_status=false&grouping=default';
    }
    const filterUpdates = root.CRT.getQueryParams(
      root.location.search,
      Object.keys(root.CRT.initialFilterState)
    );

    Object.keys(root.CRT.initialFilterState).forEach(function(key) {
      root.CRT.filterDataModel[key] = root.CRT.initialFilterState[key];
    });

    root.CRT.mutateFilterDataWithUpdates(root.CRT.filterDataModel, filterUpdates);

    filterController();
    root.CRT.initValidateTextSearch();
    root.CRT.applyArchivedCampaigns();
    root.CRT.observeCampaigns();
  }

  window.addEventListener('DOMContentLoaded', init);
})(window, document);
