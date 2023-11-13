function getSection() {
  const sectionDropdown = document.getElementById('assigned-section-label');
  return sectionDropdown?.innerText;
}
function gtag() {
  window.dataLayer = window.dataLayer || [];
  dataLayer.push(arguments);
}

function getEventName(e) {
  if (e.target.dataset.gaEventName) {
    return e.target.dataset.gaEventName;
  }
  const ariaLabel = e.target.ariaLabel?.length ? e.target.ariaLabel : 'unlabeled link element';
  const innerText = e.target.innerText?.length ? e.target.innerText : 'empty link element';
  return ariaLabel + ' ' + innerText;
}

function sendGAPublicClickEvent(e) {
  const eventName = getEventName(e);
  gtag('event', 'click', { event_name: eventName });
}

function sendGAClickEvent(e) {
  const eventName = getEventName(e);
  const section = getSection();
  gtag('event', 'click', { event_name: eventName, section: section });
}

(function(root, dom) {
  function init() {
    const relatedReportButton = dom.getElementById('related-reports');
    if (relatedReportButton !== null) {
      relatedReportButton.addEventListener('click', sendGAClickEvent);
    }
    const navItems = document.getElementsByClassName('usa-nav__primary-item');
    Array.from(navItems).forEach(navItem => {
      navItem.addEventListener('click', sendGAPublicClickEvent);
    });
    const examples = document.querySelectorAll('#crt-landing--examples .usa-nav__submenu-item');
    examples.forEach(ex => {
      ex.addEventListener('click', sendGAPublicClickEvent);
    });
    const infoButton = document.getElementById('info-link');
    if (infoButton !== null) {
      infoButton.addEventListener('click', sendGAPublicClickEvent);
    }
    const groupingButton = document.getElementById('grouping-select');
    if (groupingButton !== null) {
      groupingButton.addEventListener('change', sendGAClickEvent);
    }
  }
  window.addEventListener('DOMContentLoaded', init);
})(window, document);
