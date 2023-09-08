(function(root, dom) {
  function getSectionFromProfile() {
    return dom.getElementById('profile_section').value;
  }

  function getSectionFromParams() {
    var params = new URLSearchParams(window.location.search);
    return params.get('section');
  }

  function getDefaultSection() {
    return getSectionFromParams() || getSectionFromProfile();
  }

  function filterBySection(section) {
    dom.querySelectorAll('.filter-by-section').forEach(filterable => {
      const sectionClass = `section-${section}`;
      const isForSection = filterable.classList.contains(sectionClass);
      filterable.hidden = !isForSection;
    });
  }

  function initSectionFilter(filter) {
    const defaultSection = getDefaultSection();
    if (defaultSection) {
      filter.value = defaultSection;
      filterBySection(defaultSection);
    }

    filter.addEventListener('change', () => filterBySection(filter.value));
  }

  dom.addEventListener('DOMContentLoaded', function() {
    const sectionFilter = dom.querySelector('#id_section');
    initSectionFilter(sectionFilter);
    dom.querySelector('.notebooks').hidden = false;
  });
})(window, document);
