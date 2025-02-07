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

        const sectionDashboardsContainerElement = document.getElementById(section + "-dashboards-container");
        sectionDashboardsContainerElement.innerHTML = "";

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
            sectionDashboardsContainerElement.appendChild(buildDashboardCardHTML(dashboardData));
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
        sectionDashboardsContainerElement.dataset.pageNumber = pageNumber;
    }

    function populateInitialSectionDashboards() {
        const containers = document.getElementsByName("section-dashboards-container");
        const dashboardDataBySection = JSON.parse(document.getElementById('dashboards-by-section-data').textContent);
        for(element of containers) {
            const sectionName = element.id.split("-")[0];
            if (sectionName in dashboardDataBySection) {
                paginateSectionDashboards(sectionName, dashboardDataBySection[sectionName], parseInt(element.dataset.pageSize), parseInt(element.dataset.pageNumber));
            }
        }
    }
    
    populateInitialSectionDashboards();
})(window, document);
