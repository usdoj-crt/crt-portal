(function(root, dom) {
  function getSectionFromProfile() {
    return dom.getElementById('profile_section').value;
  }

  function getParam(key) {
    const params = new URLSearchParams(window.location.search);
    return params.get(key);
  }

  function setParam(key, value) {
    const params = new URLSearchParams(window.location.search);
    params.set(key, value);
    window.history.replaceState({}, '', `${window.location.pathname}?${params}`);
  }

  function getDefaultSection() {
    return getParam('section') || getSectionFromProfile();
  }

  function hideOrShowNotebooks(section) {
    const sectionClass = `section-${section}`;
    const notebooks = [...dom.querySelectorAll('.notebook')];
    const shouldShowNotebooks = notebooks.map(notebook => {
      if (!hasVisibleCards(notebook)) return [notebook, false];

      if (!notebook.classList.contains('filter-by-section')) {
        return [notebook, true];
      }

      return [notebook, notebook.classList.contains(sectionClass)];
    });
    shouldShowNotebooks.forEach(([notebook, shouldShow]) => {
      notebook.dataset.filtered = !shouldShow;
    });
  }

  function hasVisibleCards(element) {
    const cards = [...element.querySelectorAll('.crt-portal-card')];
    return !cards.every(card => !!card.closest('[data-filtered="true"]'));
  }

  function hideOrShowCards(section) {
    const sectionClass = `section-${section}`;
    dom.querySelectorAll('.filter-by-section').forEach(filterable => {
      if (filterable.classList.contains('notebook')) return;
      const isForSection = filterable.classList.contains(sectionClass);
      filterable.dataset.filtered = !isForSection;
    });
  }

  function hideOrShowGroups() {
    const groups = [...dom.querySelectorAll('.data-group')];
    const shouldShowGroups = groups.map(g => [g, hasVisibleCards(g)]);
    shouldShowGroups.forEach(([group, shouldShow]) => {
      group.dataset.filtered = !shouldShow;
    });
  }

  function filterBySection(section) {
    document.querySelectorAll('[data-filtered]').forEach(element => {
      element.dataset.filtered = 'false';
    });
    hideOrShowCards(section);
    hideOrShowNotebooks(section);
    hideOrShowGroups();
    applyFilters();
  }

  function initSectionFilter(filter) {
    const defaultSection = getDefaultSection();
    if (defaultSection) {
      filter.value = defaultSection;
      filterBySection(defaultSection);
    }

    filter.addEventListener('change', () => {
      filterBySection(filter.value);
      setParam('section', filter.value);
    });
  }

  function applyFilters() {
    document.querySelector('.data-content').hidden = true;
    document.querySelectorAll('[data-filtered]').forEach(element => {
      element.hidden = element.dataset.filtered === 'true';
    });
    document.querySelector('.data-content').hidden = false;
  }

  function initCityFilter(filter) {
    filter.addEventListener('change', () => {
      filterByCity(filter.value);
    });
  }

  function filterByCity(city) {
    dom.querySelectorAll('.city-wrapper').forEach(cityDataWrapper => {
        cityDataWrapper.hidden = !cityDataWrapper.classList.contains(city);
    })
  }

  dom.addEventListener('DOMContentLoaded', function() {
    const sectionFilter = dom.querySelector('#id_section');
    const cityFilter = dom.querySelector('.incident-location-city');
    initCityFilter(cityFilter);
    initSectionFilter(sectionFilter);
  });
})(window, document);
