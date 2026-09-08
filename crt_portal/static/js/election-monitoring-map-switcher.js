// Election Monitoring — administration map switcher.
//
// The page renders one map_widget per administration (all pre-booted by the
// map widget JS on load) inside panels tagged with
// `data-monitoring-admin-panel="<key>"`, plus a row of buttons tagged with
// `data-monitoring-admin="<key>"`. This shows exactly one panel at a time and
// keeps the buttons' aria-pressed state in sync. No data is fetched here — the
// maps load their own data; this only toggles visibility.
(function () {
  'use strict';

  function init() {
    var buttons = Array.prototype.slice.call(
      document.querySelectorAll('[data-monitoring-admin]')
    );
    var panels = Array.prototype.slice.call(
      document.querySelectorAll('[data-monitoring-admin-panel]')
    );

    if (!buttons.length || !panels.length) {
      return;
    }

    function select(key) {
      buttons.forEach(function (button) {
        button.setAttribute(
          'aria-pressed',
          button.dataset.monitoringAdmin === key ? 'true' : 'false'
        );
      });
      panels.forEach(function (panel) {
        panel.hidden = panel.dataset.monitoringAdminPanel !== key;
      });
    }

    buttons.forEach(function (button) {
      button.addEventListener('click', function () {
        select(button.dataset.monitoringAdmin);
      });
    });

    // Each map dispatches `map-widget:loaded` (bubbling) when it finishes.
    // Remove that panel's loading indicator when its map is ready.
    panels.forEach(function (panel) {
      panel.addEventListener('map-widget:loaded', function () {
        var loading = panel.querySelector('.spinner');
        if (loading) {
          loading.remove();
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
