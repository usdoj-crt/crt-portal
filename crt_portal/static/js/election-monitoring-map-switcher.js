// Election Monitoring — administration map switcher.
//
// The page renders one map_widget per administration inside panels tagged with
// `data-monitoring-admin-panel="<key>"`, plus a row of buttons tagged with
// `data-monitoring-admin="<key>"`. This shows exactly one panel at a time and
// keeps the buttons' aria-pressed state in sync.
//
// The maps are lazy-loaded (data-map-lazy-load): the widget JS does NOT boot
// them on page load, so this switcher boots each map (via window.UsaMapWidget)
// the first time its panel is revealed — the default panel on load, the rest
// on first click. Booting is idempotent, so re-showing a panel is a no-op.
(function() {
  'use strict';

  function init() {
    var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-monitoring-admin]'));
    var panels = Array.prototype.slice.call(
      document.querySelectorAll('[data-monitoring-admin-panel]')
    );

    if (!buttons.length || !panels.length) {
      return;
    }

    function bootPanel(panel) {
      var widget = panel.querySelector('.usa-map-widget');
      if (widget && window.UsaMapWidget && window.UsaMapWidget.init) {
        window.UsaMapWidget.init(widget);
      }
    }

    function select(key) {
      buttons.forEach(function(button) {
        button.setAttribute(
          'aria-pressed',
          button.dataset.monitoringAdmin === key ? 'true' : 'false'
        );
      });
      panels.forEach(function(panel) {
        var isActive = panel.dataset.monitoringAdminPanel === key;
        panel.hidden = !isActive;
        if (isActive) {
          // idempotent - by design
          // The map only loads the first
          // time this is called
          bootPanel(panel);
        }
      });
    }

    buttons.forEach(function(button) {
      button.addEventListener('click', function() {
        select(button.dataset.monitoringAdmin);
      });
    });

    // Each map dispatches `map-widget:loaded` (bubbling) when it finishes.
    // Remove that panel's loading indicator when its map is ready.
    panels.forEach(function(panel) {
      panel.addEventListener('map-widget:loaded', function() {
        var loading = panel.querySelector('.spinner');
        if (loading) {
          loading.remove();
        }
      });
    });

    // On load nothing is clicked, so boot the panel that's
    // initially visible on the page (does not have hidden)
    var initialPanel = panels.filter(function(panel) {
      return !panel.hidden;
    })[0];
    if (initialPanel) {
      bootPanel(initialPanel);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
