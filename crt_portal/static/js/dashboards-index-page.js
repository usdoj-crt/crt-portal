(function(root, dom) {
    function buildDashboardCardHTML(dashboardData) {
        const dashboardCardElement = document.createElement('li');
        dashboardCardElement.classList.add("usa-card");

        const dashboardHTML = `
            <div class="usa-card__container">
                <div class="usa-card__header">
                    <a href="${dashboardData.url}" class="usa-card__heading usa-link">
                    ${dashboardData.name}
                    </a>
                </div>
                <div class="usa-card__body">
                    <p>
                    ${dashboardData.description}
                    </p>
                </div>
                <div class="usa-card__footer">
                    <hr>
                    <p>
                        Last Modified: ${new Date(dashboardData.last_modified).toLocaleString('en-US', {hour12: false})}
                    </p>
                </div>
            </div>
        `;
        dashboardCardElement.innerHTML = dashboardHTML
        return dashboardCardElement;
    }

    function paginateSectionDashboards(section, dashboardsList, pageSize, pageNumber) {
        const startIndex = pageNumber * pageSize;
        const endIndex = (pageNumber + 1) * pageSize;
        const numberOfPages = Math.ceil(dashboardsList.length / pageSize);

        const sectionDashboardsCardsContainerElement = document.getElementById(section + "-dashboards-cards-container");
        sectionDashboardsCardsContainerElement.innerHTML = "";

        const paginationPrevious = document.getElementById(section + "-dashboards-previous");
        paginationPrevious.style.display = "none";
        if (pageNumber > 0) {
            paginationPrevious.addEventListener('click', function thisCallback() {
                paginateSectionDashboards(section, dashboardsList, pageSize, pageNumber - 1);
                this.removeEventListener('click', thisCallback);
            });
            paginationPrevious.style.display = "flex"
        }

        dashboardsList.slice(startIndex, endIndex).forEach((dashboardData) => {
            sectionDashboardsCardsContainerElement.appendChild(buildDashboardCardHTML(dashboardData));
        });

        const paginationNext = document.getElementById(section + "-dashboards-next");
        paginationNext.style.display = "none";
        if (pageNumber < numberOfPages - 1) {
            paginationNext.addEventListener('click', function thisCallback(){
                paginateSectionDashboards(section, dashboardsList, pageSize, pageNumber + 1);
                this.removeEventListener('click', thisCallback);
            });
            paginationNext.style.display = "flex";
        }

        const pageNumberElement = document.getElementById(section + "-dashboards-page-number");
        if (numberOfPages != 1) {
            const displayedPageNumber = pageNumber + 1;
            pageNumberElement.textContent = displayedPageNumber.toLocaleString();
            pageNumberElement.style.display = "flex";
        } else {
            pageNumberElement.style.display = "none";
        }
        sectionDashboardsCardsContainerElement.dataset.pageNumber = pageNumber;
    }

    function handleFilterBySection(section) {
        const containers = document.getElementsByName("section-dashboards-container");
        for(const containerElement of containers) {
            if (!section) {
                containerElement.style.display = "block";
                continue;
            }

            if (containerElement === document.getElementById(section + "-dashboards-container")) {
                containerElement.style.display = "block";
            } else {
                containerElement.style.display = "none";
            }
        }
    }

    function populateInitialSectionDashboards() {
        const dashboardDataBySection = JSON.parse(document.getElementById('dashboards-by-section-data').textContent);
        const containers = document.getElementsByName("section-dashboards-cards-container");
        for(const cardsContainerElement of containers) {
            const sectionName = cardsContainerElement.id.split("-")[0];
            if (sectionName in dashboardDataBySection) {
                paginateSectionDashboards(sectionName, dashboardDataBySection[sectionName], parseInt(cardsContainerElement.dataset.pageSize), parseInt(cardsContainerElement.dataset.pageNumber));
            }
        }
    }

    function setupDashboardFilterSelect() {
        const dashboardsFilterSelectElement = document.getElementById('dashboards-filter-section-select');
        dashboardsFilterSelectElement.addEventListener('change', (event) => {
            handleFilterBySection(dashboardsFilterSelectElement.value);
        });
    }

    populateInitialSectionDashboards();
    setupDashboardFilterSelect();
})(window, document);
