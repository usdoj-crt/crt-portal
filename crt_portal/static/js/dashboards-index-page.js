(function(root, dom) {
    function buildDashboardCardHTML(dashboardData) {
        let dashboardCardElement = document.createElement('li');
        dashboardCardElement.classList.add("usa-card", "tablet-lg:grid-col-6", "widescreen:grid-col-4");

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

    function buildDashboardPaginationButton(type, number) {
        let paginationElement = document.createElement('a');

        switch(type) {
            case "forward":
                paginationElement.classList.add("usa-pagination__link", "usa-pagination__next-page");
                const paginationNextHTML = `
                    <span class="usa-pagination__link-text" aria-label="Next page">Next </span>
                    <img src="/static/img/usa-icons/navigate_next.svg"></img>
                `;
                paginationElement.innerHTML = paginationNextHTML;
                break;
            case "backward":
                paginationElement.classList.add("usa-pagination__link", "usa-pagination__previous-page");
                const paginationPreviousHTML = `
                    <img src="/static/img/usa-icons/navigate_before.svg"></img>
                    <span class="usa-pagination__link-text" aria-label="Previous page">Previous</span>
                `;
                paginationElement.innerHTML = paginationPreviousHTML;
                break;
            case "number":
                paginationElement.classList.add("usa-pagination__button");
                paginationElement.textContent = number.toString();
                break;
        }
        return paginationElement;
    }

    function paginateSectionDashboards(section, dashboardsList, pageSize, pageNumber) {
        console.log("Paginating Dashboards for section: ", section);
        console.log("dashboardsList = ", dashboardsList);
        console.log("pageSize = ", pageSize);
        console.log("pageNumber = ", pageNumber);

        const startIndex = pageNumber * pageSize;
        const endIndex = (pageNumber + 1) * pageSize;

        let numberOfPages = Math.ceil(dashboardsList.length / pageSize);

        console.log("numberOfPages = ", numberOfPages);

        const sectionDashboardsContainerElement = document.getElementById(section + "-dashboards-container");
        sectionDashboardsContainerElement.innerHTML = "";

        if (pageNumber > 0) {
            let paginationPrevious = buildDashboardPaginationButton("backward");
            paginationPrevious.addEventListener('click', function(event) {
                paginateSectionDashboards(section, dashboardsList, pageSize, pageNumber - 1);
            });

            sectionDashboardsContainerElement.appendChild(paginationPrevious);
        }

        dashboardsList.slice(startIndex, endIndex).forEach((dashboardData) => {
            sectionDashboardsContainerElement.appendChild(buildDashboardCardHTML(dashboardData));
        });

        if (pageNumber < numberOfPages - 1) {
            let paginationNext = buildDashboardPaginationButton("forward");
            paginationNext.addEventListener('click', function(event){
                paginateSectionDashboards(section, dashboardsList, pageSize, pageNumber + 1);
            });
            
            sectionDashboardsContainerElement.appendChild(paginationNext);
        }
    }

    function populateInitialSectionDashboards() {
        console.log("Doing Initial Pagination of Section Dashboards...");
        const containers = document.getElementsByName("section-dashboards-container");

        const dashboardDataBySection = JSON.parse(document.getElementById('dashboards-by-section-data').textContent);
        console.log("Dashboards Data = ", dashboardDataBySection);

        for(element of containers) {
            console.log("Element = ", element);
            const sectionName = element.id.split("-")[0];
            if (sectionName in dashboardDataBySection) {
                paginateSectionDashboards(sectionName, dashboardDataBySection[sectionName], parseInt(element.dataset.pageSize), parseInt(element.dataset.pageNumber));
            }
        }
    }
    
    populateInitialSectionDashboards();
})(window, document);
