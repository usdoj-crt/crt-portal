(function(root, dom) {
  function buildDashboardCardHTML(dashboardData) {
    const dashboardCardElement = document.createElement('li');
    dashboardCardElement.classList.add('usa-card', 'flex-fill');

    const dashboardHTML = `
            <div class="usa-card__container margin-left-0">
                <div class="usa-card__header">
                    <a href="${dashboardData.url}" class="usa-card__heading usa-link">
                    ${dashboardData.name}
                    </a>
                </div>
                <div class="usa-card__body">
                    <p class="font-body-md">
                    ${dashboardData.description}
                    </p>
                </div>
                <div class="usa-card__footer">
                    <p class="font-body-3xs">
                        Last Modified: ${new Date(dashboardData.last_modified).toLocaleString(
                          'en-US',
                          { hour12: false }
                        )}
                    </p>
                </div>
            </div>
        `;
    dashboardCardElement.innerHTML = dashboardHTML;
    return dashboardCardElement;
  }

  function paginateSectionDashboards(section, dashboardsList, pageSize, pageNumber) {
    const startIndex = pageNumber * pageSize;
    const endIndex = (pageNumber + 1) * pageSize;
    const numberOfPages = Math.ceil(dashboardsList.length / pageSize);

    const sectionDashboardsCardsContainerElement = document.getElementById(
      section + '-dashboards-cards-container'
    );
    sectionDashboardsCardsContainerElement.innerHTML = '';
    dashboardsList.slice(startIndex, endIndex).forEach(dashboardData => {
      sectionDashboardsCardsContainerElement.appendChild(buildDashboardCardHTML(dashboardData));
    });

    const sectionPaginationContainer = document.getElementById(
      section + '-dashboards-pagination-container'
    );
    const pageNumberElement = document.getElementById(section + '-dashboards-current-page');
    sectionPaginationContainer.style.display = 'none';
    pageNumberElement.style.display = 'none';
    if (numberOfPages != 1) {
      sectionPaginationContainer.style.display = 'flex';
      const lastPageElement = document.getElementById(section + '-dashboards-last-page');
      lastPageElement.textContent = numberOfPages.toString();

      const displayedPageNumber = pageNumber + 1;
      pageNumberElement.textContent = displayedPageNumber.toLocaleString();
      pageNumberElement.style.display = 'flex';
    }

    const paginationPrevious = document.getElementById(section + '-dashboards-previous');
    paginationPrevious.style.display = 'none';
    if (pageNumber > 0) {
      paginationPrevious.style.display = 'flex';
    }

    const paginationNext = document.getElementById(section + '-dashboards-next');
    paginationNext.style.display = 'none';
    if (pageNumber < numberOfPages - 1) {
      paginationNext.style.display = 'flex';
    }
    sectionDashboardsCardsContainerElement.dataset.currentPage = pageNumber;
    sectionDashboardsCardsContainerElement.dataset.lastPage = numberOfPages - 1;
  }

  function handleFilterBySection(section) {
    const containers = document.getElementsByName('section-dashboards-container');
    containers.forEach(c => (c.hidden = !!section));
    if (!section) return;
    document.getElementById(`${section}-dashboards-container`).hidden = false;
  }

  function handleDashboardsPaginationNextPrevious(section, forward = true) {
    const dashboardDataBySection = JSON.parse(
      document.getElementById('dashboards-by-section-data').textContent
    );
    const dashboardsList = dashboardDataBySection[section];

    const sectionDashboardsCardsContainerElement = document.getElementById(
      section + '-dashboards-cards-container'
    );
    const currentPageNumber = parseInt(sectionDashboardsCardsContainerElement.dataset.currentPage);
    const pageSize = parseInt(sectionDashboardsCardsContainerElement.dataset.pageSize);

    const direction = forward ? 1 : -1;
    paginateSectionDashboards(section, dashboardsList, pageSize, currentPageNumber + direction);
  }

  function handleDashboardsPaginateToPage(section, page) {
    const dashboardDataBySection = JSON.parse(
      document.getElementById('dashboards-by-section-data').textContent
    );
    const dashboardsList = dashboardDataBySection[section];

    const sectionDashboardsCardsContainerElement = document.getElementById(
      section + '-dashboards-cards-container'
    );
    const pageSize = parseInt(sectionDashboardsCardsContainerElement.dataset.pageSize);
    paginateSectionDashboards(section, dashboardsList, pageSize, page);
  }

  function setupSectionPaginationButtons(section) {
    const paginationPrevious = document.getElementById(section + '-dashboards-previous');
    paginationPrevious.addEventListener('click', () => {
      handleDashboardsPaginationNextPrevious(section, false);
    });

    const paginationFirst = document.getElementById(section + '-dashboards-first-page');
    paginationFirst.addEventListener('click', () => {
      handleDashboardsPaginateToPage(section, 0);
    });

    const sectionDashboardsCardsContainerElement = document.getElementById(
      section + '-dashboards-cards-container'
    );
    const paginationLast = document.getElementById(section + '-dashboards-last-page');
    paginationLast.addEventListener('click', () => {
      handleDashboardsPaginateToPage(
        section,
        parseInt(sectionDashboardsCardsContainerElement.dataset.lastPage)
      );
    });

    const paginationNext = document.getElementById(section + '-dashboards-next');
    paginationNext.addEventListener('click', () => {
      handleDashboardsPaginationNextPrevious(section);
    });
  }

  function populateInitialSectionDashboards() {
    const dashboardDataBySection = JSON.parse(
      document.getElementById('dashboards-by-section-data').textContent
    );
    const containers = document.getElementsByName('section-dashboards-cards-container');
    for (const cardsContainerElement of containers) {
      const sectionName = cardsContainerElement.id.split('-')[0];
      if (dashboardDataBySection.hasOwnProperty(sectionName)) {
        paginateSectionDashboards(
          sectionName,
          dashboardDataBySection[sectionName],
          parseInt(cardsContainerElement.dataset.pageSize),
          parseInt(cardsContainerElement.dataset.currentPage)
        );
        setupSectionPaginationButtons(sectionName);
      }
    }
  }

  function setupDashboardFilterSelect() {
    const dashboardsFilterSelectElement = document.getElementById(
      'dashboards-filter-section-select'
    );
    dashboardsFilterSelectElement.addEventListener('change', event => {
      handleFilterBySection(dashboardsFilterSelectElement.value);
    });
  }

  populateInitialSectionDashboards();
  setupDashboardFilterSelect();
})(window, document);
