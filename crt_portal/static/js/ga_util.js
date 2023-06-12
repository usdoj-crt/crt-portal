function getSection() {
  const sectionDropdown = document.getElementById('assigned-section-label');
  return sectionDropdown?.innerText;
}
function gtag() {
  window.dataLayer = window.dataLayer || [];
  dataLayer.push(arguments);
}

export function sendGAPublicClickEvent(event_name) {
  gtag('event', 'click', { event_name: event_name });
}

export function sendGAClickEvent(event_name) {
  const section = getSection();
  gtag('event', 'click', { event_name: event_name, section: section });
}

export function sendGAFilterEvent(params) {
  const section = getSection();
  gtag('event', 'search_filter', { filters: params, section: section });
}

(function(root, dom) {
  function init() {
    const relatedReportButton = dom.getElementById('related-report');
    if (relatedReportButton !== null) {
      relatedReportButton.addEventListener('click', sendGAClickEvent('view related reports'));
    }
  }
  window.addEventListener('DOMContentLoaded', init);
})(window, document);
