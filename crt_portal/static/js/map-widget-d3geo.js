// MapWidget (d3-geo)

const DC_BADGE = {
  code: 'DC',
  name: 'District of Columbia',
  label: 'DC',
  cx: 890,
  cy: 270
};

const VIEWBOX_WIDTH = 960;
const VIEWBOX_HEIGHT = 600;

// Horizontal/vertical gap between the cursor and the tooltip.
const TOOLTIP_OFFSET = 16;

// Format an "M/D/YYYY" date string as "Mon dd, YYYY" (e.g. "Jul 22, 2025").
// Parses the components directly to avoid any timezone conversion.
const MONTH_ABBREVIATIONS = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec'
];

// Create a DOM element with an optional class name.
function createElement(tag, className) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  return node;
}

function formatActionDate(dateString) {
  const parts = dateString.split('/');
  if (parts.length !== 3) {
    return dateString;
  }
  const month = parseInt(parts[0], 10);
  const day = parseInt(parts[1], 10);
  const year = parseInt(parts[2], 10);
  if (!month || !day || !year || month < 1 || month > 12) {
    return dateString;
  }
  const paddedDay = String(day).padStart(2, '0');
  return `${MONTH_ABBREVIATIONS[month - 1]} ${paddedDay}, ${year}`;
}

// Returns a sortable number key derived from an action's "M/D/YYYY" date.
// Undated/invalid evaluates to -> -1
// so undated actions sort last when ordering
// by latest date first.
function getActionSortKey(action) {
  const parts = String(action?.date ?? '').split('/');
  if (parts.length !== 3) return -1;
  const month = parseInt(parts[0], 10);
  const day = parseInt(parts[1], 10);
  const year = parseInt(parts[2], 10);
  if (!month || !day || !year) return -1;
  return year * 10000 + month * 100 + day;
}

// Create the SVG element the map will be drawn into.
function createMapSvg(mapElement) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', 'map-widget__svg');

  // Hide the map from screen readers. SVGs are not reliably accessible
  // so, we provide a separate set of keyboard/screen-reader controls
  // that fully replicate the map's interactivity.
  // see: buildAccessibleControls
  svg.setAttribute('aria-hidden', 'true');
  mapElement.appendChild(svg);
  return svg;
}

/**
 * Collects the unique set of action categories across data actions,
 * sorted alphabetically. Used to render the (optional) category bar.
 * Returns [] if no actions have categories.
 */
function collectCategories(data) {
  const seen = new Set();
  for (const state of Object.values(data)) {
    for (const action of state.actions || []) {
      if (action.category) {
        seen.add(action.category);
      }
    }
  }
  return Array.from(seen).sort();
}

/**
 * Tallies a list of actions by their category. Returns an object mapping each
 * category to its count; actions without a category are ignored. Shared by the
 * per-state category bar and the (optional) nationwide summary view.
 */
function countActionsByCategory(actions) {
  const counts = {};
  for (const action of actions || []) {
    if (action.category) {
      counts[action.category] = (counts[action.category] || 0) + 1;
    }
  }
  return counts;
}

// Create the category summary bar, hidden until a state is selected. Builds the
// static structure (header with the caption text/total label, plus the slots
// container); the per-state pieces (state-name prefix, total count, and the
// category slots) are filled in by renderCategoryBar.
function createCategoryBar(container, mapConfig) {
  const bar = createElement('div', 'map-widget__category-bar');
  bar.hidden = true;
  // The panel (aria-live) already announces the selected state's actions,
  // so treat this bar as a purely visual summary to avoid double-announcing.
  bar.setAttribute('aria-hidden', 'true');

  // Header row: caption on the left, total on the right, all optional. The
  // static pieces (the caption text and the total label) are set here since
  // they never change; the per-state pieces (the caption's state-name prefix
  // and the total count) are filled in by renderCategoryBar.
  if (
    mapConfig.categoryBarCaption ||
    mapConfig.captionStateText ||
    mapConfig.categoryBarTotalLabel
  ) {
    const header = createElement('div', 'map-widget__category-bar-header');

    if (mapConfig.categoryBarCaption || mapConfig.captionStateText) {
      const caption = createElement('span', 'map-widget__category-bar-caption');

      if (mapConfig.captionStateText) {
        const stateClasses = ['map-widget__category-bar-caption-state'];
        if (mapConfig.captionStateClasses) {
          stateClasses.push(mapConfig.captionStateClasses);
        }
        const stateEl = createElement('span', stateClasses.join(' '));
        caption.appendChild(stateEl);
      }

      if (mapConfig.categoryBarCaption) {
        const textClasses = ['map-widget__category-bar-caption-text'];
        if (mapConfig.categoryBarCaptionClasses) {
          textClasses.push(mapConfig.categoryBarCaptionClasses);
        }
        const textEl = createElement('span', textClasses.join(' '));
        textEl.textContent = mapConfig.categoryBarCaption;
        caption.appendChild(textEl);
      }

      header.appendChild(caption);
    }

    if (mapConfig.categoryBarTotalLabel) {
      const total = createElement('span', 'map-widget__category-bar-total');

      const totalLabelClasses = ['map-widget__category-bar-total-label'];
      if (mapConfig.categoryBarTotalLabelClasses) {
        totalLabelClasses.push(mapConfig.categoryBarTotalLabelClasses);
      }
      const totalLabel = createElement('span', totalLabelClasses.join(' '));
      totalLabel.textContent = mapConfig.categoryBarTotalLabel;

      const totalCountClasses = ['map-widget__category-bar-total-count'];
      if (mapConfig.categoryBarTotalCountClasses) {
        totalCountClasses.push(mapConfig.categoryBarTotalCountClasses);
      }
      const totalCount = createElement('span', totalCountClasses.join(' '));

      total.appendChild(totalCount);
      total.appendChild(totalLabel);
      header.appendChild(total);
    }

    bar.appendChild(header);
  }

  // Slots container, filled per-state by renderCategoryBar.
  const slots = createElement('div', 'map-widget__category-slots');
  bar.appendChild(slots);

  container.appendChild(bar);
  return bar;
}

// Create the hover tooltip element, hidden until shown. It's positioned
// relative to the map area, so it's appended inside `.map-widget__map`.
function createTooltip(mapElement) {
  const tooltip = createElement('div', 'map-widget__tooltip');
  tooltip.setAttribute('aria-hidden', 'true');
  tooltip.hidden = true;
  mapElement.appendChild(tooltip);
  return tooltip;
}

// Show the tooltip for a feature: fill in its name + code, then position it.
function showTooltip(context, feature, event) {
  const tooltip = context.tooltip;
  if (!tooltip) {
    return;
  }

  const code = feature.properties.code;
  const name = context.data?.[code]?.name ?? feature.properties.name;

  tooltip.innerHTML = '';

  const tooltipName = createElement('span', 'map-widget__tooltip-name');
  tooltipName.textContent = name;
  tooltip.appendChild(tooltipName);

  const tooltipBadge = createElement('span', 'map-widget__state-badge');
  tooltipBadge.textContent = code;
  tooltip.appendChild(tooltipBadge);

  tooltip.hidden = false;
  moveTooltip(context, event);
}

// Position the tooltip next to the cursor, measured relative to the map area.
function moveTooltip(context, mouseEvent) {
  const tooltip = context.tooltip;
  if (!tooltip || tooltip.hidden) {
    return;
  }

  const mapElement = tooltip.parentElement;
  const bounds = mapElement.getBoundingClientRect();
  const x = mouseEvent.clientX - bounds.left;
  const y = mouseEvent.clientY - bounds.top;

  // If a right-side tooltip would overflow the map's right edge, flip it to the
  // left of the cursor so it stays within the (overflow-clipped) map area.
  const overflowsRight = x + TOOLTIP_OFFSET + tooltip.offsetWidth > bounds.width;
  const left = overflowsRight ? x - TOOLTIP_OFFSET - tooltip.offsetWidth : x + TOOLTIP_OFFSET;

  // Likewise flip above the cursor when we would overflow the bottom edge. When
  // the category bar is visible it sits at the bottom of the map area, so treat
  // its top as the boundary to keep the tooltip from disappearing behind it.
  const categoryBar = context.categoryBar;
  let bottomBoundary = bounds.height;
  if (categoryBar && categoryBar.offsetHeight > 0) {
    bottomBoundary = categoryBar.getBoundingClientRect().top - bounds.top;
  }
  const overflowsBottom = y + TOOLTIP_OFFSET + tooltip.offsetHeight > bottomBoundary;
  const top = overflowsBottom ? y - TOOLTIP_OFFSET - tooltip.offsetHeight : y + TOOLTIP_OFFSET;

  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
}

function hideTooltip(context) {
  if (context.tooltip) {
    context.tooltip.hidden = true;
  }
}

function getMapConfig(mapWidget) {
  const mapConfig = {};

  mapConfig.defaultFillColor = mapWidget?.dataset?.mapDefaultFillColor || '#3498db';

  mapConfig.activeFillColor = mapWidget?.dataset?.mapActiveFillColor || '#f4c430';

  mapConfig.strokeColor = mapWidget?.dataset?.mapStrokeColor || '#ffffff';

  mapConfig.strokeWidth = mapWidget?.dataset?.mapStrokeWidth || '1';

  mapConfig.badgeTextColor = mapWidget?.dataset?.mapBadgeTextColor || '#ffffff';

  mapConfig.badgeRadius = mapWidget?.dataset?.mapBadgeRadius || '16';

  mapConfig.showTooltip = mapWidget?.dataset?.mapShowTooltip === 'true';

  mapConfig.openInNewTab = mapWidget?.dataset?.mapOpenInNewTab === 'true';

  mapConfig.showCategoryBar = mapWidget?.dataset?.mapShowCategoryBar === 'true';

  mapConfig.categoryBarCaption = mapWidget?.dataset?.mapCategoryBarCaption || '';

  mapConfig.categoryBarCaptionClasses = mapWidget?.dataset?.mapCategoryBarCaptionClasses || '';

  mapConfig.captionStateText = mapWidget?.dataset?.mapCaptionStateText || '';

  mapConfig.captionStateClasses = mapWidget?.dataset?.mapCaptionStateClasses || '';

  mapConfig.categorySlotLabelClasses = mapWidget?.dataset?.mapCategorySlotLabelClasses || '';

  mapConfig.categorySlotCountClasses = mapWidget?.dataset?.mapCategorySlotCountClasses || '';

  mapConfig.categorySlotEmptyLabelClasses =
    mapWidget?.dataset?.mapCategorySlotEmptyLabelClasses || '';

  mapConfig.categorySlotEmptyCountClasses =
    mapWidget?.dataset?.mapCategorySlotEmptyCountClasses || '';

  mapConfig.categoryBarTotalLabel = mapWidget?.dataset?.mapCategoryBarTotalLabel || '';

  mapConfig.categoryBarTotalLabelClasses =
    mapWidget?.dataset?.mapCategoryBarTotalLabelClasses || '';

  mapConfig.categoryBarTotalCountClasses =
    mapWidget?.dataset?.mapCategoryBarTotalCountClasses || '';

  mapConfig.showSummary = mapWidget?.dataset?.mapShowSummary === 'true';

  mapConfig.summaryHeadingText = mapWidget?.dataset?.mapSummaryHeadingText || '';

  mapConfig.summaryBadgeText = mapWidget?.dataset?.mapSummaryBadgeText || '';

  mapConfig.summaryCategoryLabelClasses = mapWidget?.dataset?.mapSummaryCategoryLabelClasses || '';

  mapConfig.summaryCategoryCountClasses = mapWidget?.dataset?.mapSummaryCategoryCountClasses || '';

  mapConfig.summaryItemClasses = mapWidget?.dataset?.mapSummaryItemClasses || '';

  mapConfig.summaryListClasses = mapWidget?.dataset?.mapSummaryListClasses || '';

  mapConfig.summaryTotalText = mapWidget?.dataset?.mapSummaryTotalText || '';

  mapConfig.summaryTotalClasses = mapWidget?.dataset?.mapSummaryTotalClasses || '';

  mapConfig.summaryTotalCountClasses = mapWidget?.dataset?.mapSummaryTotalCountClasses || '';

  return mapConfig;
}

function getInfoPanelConfig(mapWidget) {
  const infoPanelConfig = {};

  infoPanelConfig.placeholderText = mapWidget?.dataset?.infoPanelPlaceholderText || '';

  infoPanelConfig.placeholderTextNoHover =
    mapWidget?.dataset?.infoPanelPlaceholderTextNoHover || '';

  infoPanelConfig.headingClasses = mapWidget?.dataset?.infoPanelHeadingClasses || '';

  infoPanelConfig.subheadingText = mapWidget?.dataset?.infoPanelSubheadingText || '';

  infoPanelConfig.subheadingClasses = mapWidget?.dataset?.infoPanelSubheadingClasses || '';

  infoPanelConfig.listClasses = mapWidget?.dataset?.infoPanelListClasses || '';

  infoPanelConfig.listItemClasses = mapWidget?.dataset?.infoPanelListItemClasses || '';

  infoPanelConfig.actionTextClasses = mapWidget?.dataset?.infoPanelActionTextClasses || '';

  infoPanelConfig.actionDateClasses = mapWidget?.dataset?.infoPanelActionDateClasses || '';

  infoPanelConfig.noDataText = mapWidget?.dataset?.infoPanelNoDataText || '';

  infoPanelConfig.noDataParagraphClasses =
    mapWidget?.dataset?.infoPanelNoDataParagraphClasses || '';

  const parsedMax = parseInt(mapWidget?.dataset?.infoPanelMaxItems, 10);
  infoPanelConfig.maxItems = Number.isNaN(parsedMax) ? null : parsedMax;

  infoPanelConfig.overflowText = mapWidget.dataset?.infoPanelOverflowText || '';

  infoPanelConfig.overflowClasses = mapWidget?.dataset?.infoPanelOverflowClasses || '';

  infoPanelConfig.sortOrder = mapWidget?.dataset?.infoPanelSortOrder === 'asc' ? 'asc' : 'desc';

  return infoPanelConfig;
}

// Read a comma-separated list from a data attribute; [] if missing.
function getDataAttributeUrlList(mapWidget, attributeName) {
  const value = mapWidget.dataset[attributeName] || '';
  if (value === '') {
    return [];
  }
  return value.split(',');
}

// Fetch every GeoJSON file and merge all their features into one array.
async function loadGeoJsonFeatures(urls) {
  let features = [];

  for (const url of urls) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load GeoJSON "${url}" (HTTP ${response.status})`);
    }
    const geojson = await response.json();
    features = features.concat(geojson.features);
  }

  return features;
}

// Create the d3 projection + path generator, fitted to the SVG size.
function createD3ProjectionAndPathGenerator(width, height, features) {
  const projection = d3.geoAlbersUsa();
  const d3PathGenerator = d3.geoPath(projection);

  projection.fitSize([width, height], {
    type: 'FeatureCollection',
    features: features
  });

  return d3PathGenerator;
}

// Load the JSON data file named in the widget's data-data-src attribute.
// If the fetch fails (missing record, network error, bad JSON), fall back to
// an empty data set so the map still renders, with every feature showing the
// "no data" state.
async function loadData(mapWidget) {
  const url = mapWidget.dataset.dataSrc;
  try {
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    return {};
  }
}

// Load the agency-to-image badge mapping named in the widget's
// data-badge-mapping-src attribute. Returns {} if the attribute is missing or
// the file cannot be loaded, so the caller can safely fall back to text badges.
async function loadBadgeMapping(mapWidget) {
  const url = mapWidget.dataset.badgeMappingSrc;
  if (!url) {
    return {};
  }

  try {
    const response = await fetch(url);
    if (!response.ok) {
      console.warn(
        `MapWidget: could not load badge mapping "${url}" (HTTP ${response.status}). Falling back to text badges.`
      );
      return {};
    }
    const mapping = await response.json();

    // Resolve each image path relative to the mapping file's own URL so the
    // entries stay environment-agnostic (they work whether the static root
    // is served locally or from an absolute CDN URL).
    const resolved = {};
    for (const [agency, imagePath] of Object.entries(mapping)) {
      resolved[agency] = imagePath
        ? new URL(imagePath, new URL(url, window.location.href)).href
        : imagePath;
    }
    return resolved;
  } catch (error) {
    console.warn(
      `MapWidget: could not load badge mapping "${url}". Falling back to text badges.`,
      error
    );
    return {};
  }
}

// Preload the badges images browser cache and decode each seal once so when
// we show an agency badge, we don't pause to fetch/decode the image. Iterates the
// mapping per agency (rather than per URL) so we can report exactly which
// agencies have a broken or missing seal. Returns a Set of those agency codes
// so that the badge cache can fall straight to a text badge for them.
async function preloadBadgeImages(badgeMapping) {
  const brokenAgencies = new Set();

  const entries = Object.entries(badgeMapping).filter(([, url]) => url);
  await Promise.all(
    entries.map(async ([agency, url]) => {
      const image = new Image();
      image.src = url;
      // decode() resolves once the image is fully decoded, and
      // rejects if the image failed to load (e.g. a 404).
      try {
        await image.decode();
      } catch {
        brokenAgencies.add(agency);
      }
    })
  );

  return brokenAgencies;
}

function showActive(path, mapConfig) {
  path.style.fill = mapConfig?.activeFillColor || '#f4c430';
}

function hideActive(path, mapConfig) {
  path.style.fill = mapConfig?.defaultFillColor || '#3498db';
}

// Make `shape` the single active shape: restore the previously active shape (if
// any) to its resting state, highlight the new one, render its info, and record
// it on the context so it stays active after the pointer leaves.
function setActive(context, shape, feature) {
  if (context.active && context.active.shape !== shape) {
    hideActive(context.active.shape, context.mapConfig);
  }

  showActive(shape, context.mapConfig);
  renderInfo(context, feature);
  renderCategoryBar(context, feature);

  context.active = { shape: shape, feature: feature };
}

// Clear the active (hovered/selected) feature: reset its fill, drop the active
// reference, restore the info-panel placeholder, and hide the category bar.
// Returns the widget to its initial "nothing selected" state.
function clearActive(context) {
  if (context.active) {
    hideActive(context.active.shape, context.mapConfig);
    context.active = null;
  }

  renderDefaultView(context);

  if (context.categoryBar) {
    context.categoryBar.hidden = true;
  }
}

// Navigate to the URL associated with a feature (from the loaded data set).
// Opens in a new tab when the open_in_new_tab option is set, otherwise in the
// current tab (the accessible default). Used by pointer clicks and
// keyboard/screen-reader activation. Hover and focus intentionally do NOT call
// this — they only highlight via setActive().
function openFeatureUrl(context, feature) {
  const stateCode = feature.properties.code;
  const url = context.data?.[stateCode]?.url;

  if (url) {
    if (context.mapConfig?.openInNewTab) {
      window.open(url, '_blank', 'noopener');
    } else {
      window.location.assign(url);
    }
  }
}

function drawFeatures(mapSvg, features, d3PathGenerator, context) {
  for (const feature of features) {
    const d = d3PathGenerator(feature);

    if (!d) {
      continue;
    }

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('class', 'map-widget__feature');
    path.setAttribute('d', d);

    path.style.stroke = context.mapConfig?.strokeColor || '#ffffff';
    path.style.strokeWidth = context.mapConfig?.strokeWidth || '2';

    path.addEventListener('mouseover', mouseEvent => {
      setActive(context, path, feature);
      showTooltip(context, feature, mouseEvent);
    });

    path.addEventListener('mousemove', mouseEvent => {
      moveTooltip(context, mouseEvent);
    });

    path.addEventListener('mouseout', () => {
      hideTooltip(context);
    });

    path.addEventListener('click', () => {
      setActive(context, path, feature);
      openFeatureUrl(context, feature);
    });

    mapSvg.appendChild(path);
    hideActive(path, context.mapConfig);

    // Register this feature so buildAccessibleControls() can create a matching
    // keyboard/screen-reader control that highlights this same shape.
    context.focusables.push({
      name: feature.properties.name,
      feature: feature,
      shape: path
    });
  }
}

function drawBadge(mapSvg, badge, context) {
  //    Create a <g> group so the circle + label share listeners.
  const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  group.setAttribute('class', 'map-widget__badge');

  //    Create the circle. Set cx, cy, r attributes from `badge`.
  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', badge.cx);
  circle.setAttribute('cy', badge.cy);
  circle.setAttribute('r', parseInt(context.mapConfig?.badgeRadius || 16)); // TODO Make me configurable
  circle.style.stroke = context.mapConfig?.strokeColor || '#ffffff';
  circle.style.strokeWidth = context.mapConfig?.strokeWidth || '2';
  group.appendChild(circle);

  //    Create the text label, centered on the circle.
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', badge.cx);
  text.setAttribute('y', badge.cy);
  text.setAttribute('text-anchor', 'middle');
  text.setAttribute('dominant-baseline', 'central');
  text.style.fill = context.mapConfig?.badgeTextColor || '#ffffff';
  text.textContent = badge.label;
  group.appendChild(text);

  //    Build the synthetic feature renderInfo expects.
  const feature = {
    properties: { code: badge.code, name: badge.name }
  };

  //    Wire the listeners as a state. On hover/click the badge becomes the
  //    single active shape and stays active after the pointer leaves.
  //    Note: pass `circle` (not the group) to setActive/hideActive,
  //    since .style.fill needs to land on the shape.
  group.addEventListener('mouseover', mouseEvent => {
    setActive(context, circle, feature);
    showTooltip(context, feature, mouseEvent);
  });

  group.addEventListener('mousemove', mouseEvent => {
    moveTooltip(context, mouseEvent);
  });

  group.addEventListener('mouseout', () => {
    hideTooltip(context);
  });

  group.addEventListener('click', () => {
    setActive(context, circle, feature);
    openFeatureUrl(context, feature);
  });

  //    Append the group to the svg, then set the resting fill.
  mapSvg.appendChild(group);
  hideActive(circle, context.mapConfig);

  //    Register the badge alongside the map features so it gets a matching
  //    keyboard/screen-reader control (see buildAccessibleControls()).
  context.focusables.push({
    name: badge.name,
    feature: feature,
    shape: circle
  });
}

function buildInfoPanel(mapWidget) {
  const panel = createElement('div', 'map-widget__panel');

  panel.setAttribute('role', 'region');
  panel.setAttribute('aria-label', 'Selected state details');

  // The actions list can get quite long, so we set assertive
  // here to ensure we interrupt when the user changes features
  panel.setAttribute('aria-live', 'assertive');
  panel.setAttribute('aria-atomic', 'true');

  mapWidget.appendChild(panel);

  return panel;
}

// Render the panel's default "nothing selected" view and keep it in sync with
// the device's hover capability. Called once after the context is ready.
function setupDefaultView(context) {
  renderDefaultView(context);

  // Re-render the default view if the device's hover capability changes (e.g. a
  // 2-in-1 switching between touchscreen and trackpad), so the placeholder
  // guidance text always matches the current primary input.
  if (typeof window.matchMedia === 'function') {
    const hoverQuery = window.matchMedia('(hover: hover)');
    hoverQuery.addEventListener('change', () => {
      // Only re-render while the default view is showing; don't clobber a
      // selected feature's details.
      if (context.panel.dataset.showingPlaceholder === 'true') {
        renderDefaultView(context);
      }
    });
  }
}

// Choose the panel's default "nothing selected" content: the summary view when
// it's enabled and the data has categories, otherwise the placeholder text.
function renderDefaultView(context) {
  if (context.mapConfig?.showSummary && context.categories) {
    renderSummary(context);
  } else {
    renderInfoPlaceholder(context.panel, context.infoPanelConfig);
  }
}

// Build a visually hidden, keyboard-focusable control for every mapped feature
// so the map is fully operable without a pointer. Native <button>s are used so
// they join the natural tab order (Tab forward, Shift+Tab backward)
// buttons are appended in alphabetical order by feature name so the tab order
// matches alphabetically descending order.
// activating a control makes its feature active — the map highlights and the
// info panel renders exactly as it does on hover.
function buildAccessibleControls(mapElement, context) {
  const controls = createElement('div', 'map-widget__sr-controls');
  controls.setAttribute('role', 'group');
  controls.setAttribute('aria-label', 'Select a state to view its enforcement actions');

  const sorted = context.focusables.slice().sort((a, b) => a.name.localeCompare(b.name));

  for (const entry of sorted) {
    const button = createElement('button', 'map-widget__sr-control');
    button.type = 'button';
    button.textContent = entry.name;

    const activate = () => setActive(context, entry.shape, entry.feature);
    button.addEventListener('focus', () => {
      activate();
      scrollWidgetIntoView(mapElement);
    });
    button.addEventListener('click', () => {
      activate();
      openFeatureUrl(context, entry.feature);
    });

    controls.appendChild(button);
  }

  mapElement.appendChild(controls);
}

// When a keyboard user Tabs onto one of the visually-hidden state controls, the
// browser's implicit focus scrolling is imprecise (the controls are 1px clipped
// elements, so it tends to over/undershoot). Scroll the widget so its top edge
// aligns with the top of the viewport instead. `scrollMarginTop` on the widget
// lets callers leave room for any fixed header.
function scrollWidgetIntoView(mapElement) {
  mapElement.scrollIntoView({ block: 'start', behavior: 'smooth' });
}

function renderInfoPlaceholder(panel, infoPanelConfig) {
  // Choose guidance text based on whether the primary input device can hover.
  // Hover-capable devices (mouse/trackpad) get the fuller "Hover ... Click ..."
  // instruction; tap/click-only devices get the click-only instruction.
  const canHover =
    typeof window.matchMedia === 'function' ? window.matchMedia('(hover: hover)').matches : true;

  const noHoverText = infoPanelConfig.placeholderTextNoHover || '';
  const hoverText = infoPanelConfig.placeholderText || '';

  panel.innerHTML = (canHover ? hoverText : noHoverText) || hoverText || '';
  panel.dataset.showingPlaceholder = 'true';
}

// Render the summary view shown when no feature is selected (opt-in via
// show_summary, and only when the data has categories): the configured heading
// and badge, then a list of every category with its total across all features.
function renderSummary(context) {
  const { panel, mapConfig, categories, data } = context;

  panel.innerHTML = '';
  panel.dataset.showingPlaceholder = 'true';

  //    Shared header (heading + pill badge + separator), using the configured
  //    summary heading/badge text (e.g. "Nationwide" / "USA").
  renderPanelHeader(context, mapConfig.summaryHeadingText, mapConfig.summaryBadgeText);

  //    Tally category totals across every feature's actions.
  const allActions = Object.values(data).flatMap(state => state.actions || []);
  const counts = countActionsByCategory(allActions);

  //    Optional total line, shown above the list (where the per-state subheading
  //    sits). The template is split on {count} so the grand total of all actions
  //    renders in its own span (independently styleable from the surrounding
  //    text).
  if (mapConfig.summaryTotalText) {
    const total = createElement('p', 'map-widget__summary-total');
    if (mapConfig.summaryTotalClasses) {
      total.className = `map-widget__summary-total ${mapConfig.summaryTotalClasses}`;
    }

    const countClass = ['map-widget__summary-total-count'];
    if (mapConfig.summaryTotalCountClasses) {
      countClass.push(mapConfig.summaryTotalCountClasses);
    }

    const parts = mapConfig.summaryTotalText.split('{count}');
    parts.forEach((part, index) => {
      // Between parts (i.e. wherever {count} appeared), insert the count span.
      if (index > 0) {
        const countEl = createElement('span', countClass.join(' '));
        countEl.textContent = allActions.length;
        total.appendChild(countEl);
      }
      if (part) {
        total.appendChild(document.createTextNode(part));
      }
    });

    panel.appendChild(total);
  }

  //    One row per category (alphabetical; context.categories is pre-sorted).
  //    Every category in the union has at least one action somewhere, so there
  //    are no zero rows to worry about here.
  const list = createElement('ul', 'map-widget__summary');
  if (mapConfig.summaryListClasses) {
    list.className = `map-widget__summary ${mapConfig.summaryListClasses}`;
  }

  const labelClasses = ['map-widget__summary-category-label'];
  if (mapConfig.summaryCategoryLabelClasses) {
    labelClasses.push(mapConfig.summaryCategoryLabelClasses);
  }
  const labelClass = labelClasses.join(' ');

  const countClasses = ['map-widget__summary-category-count'];
  if (mapConfig.summaryCategoryCountClasses) {
    countClasses.push(mapConfig.summaryCategoryCountClasses);
  }
  const countClass = countClasses.join(' ');

  const itemClasses = ['map-widget__summary-item'];
  if (mapConfig.summaryItemClasses) {
    itemClasses.push(mapConfig.summaryItemClasses);
  }
  const itemClass = itemClasses.join(' ');

  for (const category of categories) {
    const item = createElement('li', itemClass);

    const label = createElement('span', labelClass);
    label.textContent = category;

    const count = createElement('span', countClass);
    count.textContent = counts[category] || 0;

    item.appendChild(label);
    item.appendChild(count);
    list.appendChild(item);
  }

  panel.appendChild(list);
}

function createTextBadge(agency) {
  const badge = createElement('span', 'map-widget__agency-badge');
  badge.textContent = agency;
  return badge;
}

function createAgencyBadge(agency, badgeMapping) {
  const imageUrl = badgeMapping?.[agency];

  if (imageUrl && typeof imageUrl === 'string' && imageUrl !== '') {
    const image = createElement('img', 'map-widget__agency-badge-image');
    image.src = imageUrl;
    image.alt = agency;

    return image;
  }

  return createTextBadge(agency);
}

// Build the badge shown as the leading "bullet" for an action. If the agency is
// present in the badge mapping, an <img> of its seal is used; otherwise it falls
// back to the gold text badge with the agency code.
//
// Reuses previously created agency badges that were added to the cache
function getAgencyBadge(context, agency) {
  const { badgeCache, badgeMapping, brokenSeals } = context;

  // Check if the badgeCache has this agency already
  // If not, create a text badge IF the seal is 'broken'
  // otherwise, create the real agency badge.
  // Add the result to the cache
  if (!badgeCache[agency]) {
    badgeCache[agency] = brokenSeals?.has(agency)
      ? createTextBadge(agency)
      : createAgencyBadge(agency, badgeMapping);
  }

  // Reuse the cached badge
  return badgeCache[agency].cloneNode(true);
}

// Build the info-panel header — the heading (feature/summary name) and its pill
// badge, followed by the accent separator — and append it to the panel. Shared
// by the per-state view (renderInfo) and the summary view (renderSummary).
function renderPanelHeader(context, name, code) {
  const { panel, infoPanelConfig } = context;

  //    Build a flex container so the badge and heading sit side by side.
  const headingContainer = createElement('div', 'map-widget__heading-container');

  const heading = createElement('h2');
  heading.textContent = name;
  if (infoPanelConfig?.headingClasses) {
    heading.className = infoPanelConfig.headingClasses;
  }
  headingContainer.appendChild(heading);

  //    Add the small pill badge (e.g. a state's abbreviation like "CA").
  const badge = createElement('span', 'map-widget__state-badge');
  badge.textContent = code;
  headingContainer.appendChild(badge);

  panel.appendChild(headingContainer);

  //    Add the short accent bar shown beneath the heading.
  const separator = createElement('div', 'map-widget__separator');
  panel.appendChild(separator);
}

function renderInfo(context, feature) {
  const { panel, data, infoPanelConfig } = context;

  //    Resolve the state's code from the hovered/clicked feature and look up
  //    its matching record in the loaded data set.
  const stateCode = feature.properties.code;
  const stateData = data[stateCode];

  //    Clear whatever was in the panel (placeholder or a previous state).
  panel.innerHTML = '';
  panel.dataset.showingPlaceholder = 'false';

  //    Resolve the full state name (preferring the data set's name, falling
  //    back to the feature's own name).
  const stateName = stateData?.name ?? feature.properties.name;

  //    Render the shared header (heading + pill badge + separator).
  renderPanelHeader(context, stateName, stateCode);

  //    Optional subheading, shown beneath the separator. Supports the {state}
  //    placeholder.
  if (infoPanelConfig?.subheadingText) {
    const subheading = createElement('p', 'map-widget__subheading');
    if (infoPanelConfig.subheadingClasses) {
      subheading.className = `map-widget__subheading ${infoPanelConfig.subheadingClasses}`;
    }
    subheading.textContent = infoPanelConfig.subheadingText.replace('{state}', stateName);
    panel.appendChild(subheading);
  }

  //    Grab all actions, remember the true total
  const allActions = stateData?.actions ?? [];
  const total = allActions.length;

  // Sort the actions
  // Undated actions are sorted first in "asc", last in "desc"
  const sortOrder = infoPanelConfig?.sortOrder || 'desc';
  let sortedActions = [];
  if (sortOrder === 'desc') {
    sortedActions = allActions.slice().sort((a, b) => getActionSortKey(b) - getActionSortKey(a));
  } else {
    sortedActions = allActions.slice().sort((a, b) => getActionSortKey(a) - getActionSortKey(b));
  }

  const maxItems = infoPanelConfig?.maxItems;
  const actionsList = maxItems > 0 ? sortedActions.slice(0, maxItems) : sortedActions;

  if (actionsList?.length === 0) {
    const noDataParagraph = createElement('p');
    if (infoPanelConfig?.noDataParagraphClasses) {
      noDataParagraph.className = infoPanelConfig.noDataParagraphClasses;
    }
    noDataParagraph.textContent = infoPanelConfig?.noDataText || 'No data available';
    panel.appendChild(noDataParagraph);

    return;
  }

  //    Otherwise, build the list...
  const list = createElement('ul', 'map-widget__actions');
  if (infoPanelConfig?.listClasses) {
    list.className = `map-widget__actions ${infoPanelConfig.listClasses}`;
  }

  //    Add an invisible first list item that screen readers pick up so the
  //    live-region announcement leads with the state name + enforcement actions
  const srHeadingItem = createElement('li', 'map-widget__sr-only');
  srHeadingItem.textContent = `${stateName} Enforcement Actions`;
  list.appendChild(srHeadingItem);

  //    Render each action as a list item.
  for (const action of actionsList) {
    //    Create the list item wrapper.
    const item = createElement('li', 'map-widget__action');
    if (infoPanelConfig?.listItemClasses) {
      item.className = `map-widget__action ${infoPanelConfig.listItemClasses}`;
    }

    //    Create the flex row holding the agency badge and content.
    const row = createElement('div', 'map-widget__action-row');

    //    Add the agency badge, used as the row's leading "bullet". When
    //    the agency has an image in the mapping we use that; otherwise we
    //    fall back to the gold text badge.
    const badge = getAgencyBadge(context, action.agency);
    row.appendChild(badge);

    // 10d. Build the content block that holds the action text (and date).
    const content = createElement('div', 'map-widget__action-content');

    // 10e. Add the action's description text.
    const text = createElement('span', 'map-widget__action-text');
    if (infoPanelConfig?.actionTextClasses) {
      text.className = `map-widget__action-text ${infoPanelConfig.actionTextClasses}`;
    }
    text.textContent = action.action;
    // content.appendChild(text);

    // 10f. Add a formatted date when one is present.
    if (action.date !== null) {
      const date = createElement('div', 'map-widget__action-date');
      if (infoPanelConfig?.actionDateClasses) {
        date.className = `map-widget__action-date ${infoPanelConfig.actionDateClasses}`;
      }
      date.textContent = formatActionDate(action.date);
      content.appendChild(date);
    }

    content.appendChild(text);

    // 10g. Assemble the row and append the finished item to the list.
    row.appendChild(content);

    item.appendChild(row);

    list.appendChild(item);
  }

  // 11. Append the fully built actions list to the panel.
  panel.appendChild(list);

  //    When the state has more actions than we showed, add a line pointing to
  //    the full list. Supports {count} (true total) and {state} placeholders.
  if (maxItems > 0 && total > maxItems && infoPanelConfig?.overflowText) {
    const overflow = createElement('p', 'map-widget__actions-overflow');
    if (infoPanelConfig.overflowClasses) {
      overflow.className = `map-widget__actions-overflow ${infoPanelConfig.overflowClasses}`;
    }
    overflow.textContent = infoPanelConfig.overflowText
      .replace('{count}', total)
      .replace('{state}', stateName);
    panel.appendChild(overflow);
  }
}

// Fill the category bar with one slot per known category, showing how many
// of the selected state's actions fall into each. Counts use the state's
// FULL actions list (not the capped info-panel list). Every category is
// always rendered, even if the count is zero, so that the layout stays
// stable.
function renderCategoryBar(context, feature) {
  const bar = context.categoryBar;
  if (!bar) {
    return;
  }

  const { mapConfig } = context;
  const stateData = context.data[feature.properties.code];
  const actions = stateData?.actions ?? [];
  const stateName = stateData?.name ?? feature.properties.name;

  // Tally actions by category.
  const counts = countActionsByCategory(actions);

  // Fill the caption's state-name prefix — the only per-state part of the
  // caption (the static text was set once in createCategoryBar). {state} is
  // replaced with the selected state's name.
  const captionState = bar.querySelector('.map-widget__category-bar-caption-state');
  if (captionState) {
    captionState.textContent = mapConfig.captionStateText.replace('{state}', stateName);
  }

  const totalCountEl = bar.querySelector('.map-widget__category-bar-total-count');
  if (totalCountEl) {
    totalCountEl.textContent = actions.length;
  }

  // Rebuild the slots. Render every known category in alphabetical order
  // (context.categories is already sorted); dim zero counts for a stable layout.
  const slots = bar.querySelector('.map-widget__category-slots');
  slots.innerHTML = '';

  const slotLabelClasses = ['map-widget__category-slot-label'];
  if (mapConfig.categorySlotLabelClasses) {
    slotLabelClasses.push(mapConfig.categorySlotLabelClasses);
  }
  const slotLabelClass = slotLabelClasses.join(' ');

  const slotCountClasses = ['map-widget__category-slot-count'];
  if (mapConfig.categorySlotCountClasses) {
    slotCountClasses.push(mapConfig.categorySlotCountClasses);
  }
  const slotCountClass = slotCountClasses.join(' ');

  // Empty-slot variants: zero-count slots use their own base classes
  // (map-widget__category-slot-empty-label/-count) plus any configured empty
  // classes, fully replacing the normal label/count classes rather than
  // layering on top — so their styling always wins with no cascade conflict.
  const slotEmptyLabelClasses = ['map-widget__category-slot-empty-label'];
  if (mapConfig.categorySlotEmptyLabelClasses) {
    slotEmptyLabelClasses.push(mapConfig.categorySlotEmptyLabelClasses);
  }
  const slotEmptyLabelClass = slotEmptyLabelClasses.join(' ');

  const slotEmptyCountClasses = ['map-widget__category-slot-empty-count'];
  if (mapConfig.categorySlotEmptyCountClasses) {
    slotEmptyCountClasses.push(mapConfig.categorySlotEmptyCountClasses);
  }
  const slotEmptyCountClass = slotEmptyCountClasses.join(' ');

  for (const category of context.categories) {
    const count = counts[category] || 0;
    const isEmpty = count === 0;

    const slot = createElement('div', 'map-widget__category-slot');

    const label = createElement('span', isEmpty ? slotEmptyLabelClass : slotLabelClass);
    label.textContent = category;

    const value = createElement('span', isEmpty ? slotEmptyCountClass : slotCountClass);
    value.textContent = count;

    slot.appendChild(value);
    slot.appendChild(label);
    slots.appendChild(slot);
  }

  bar.hidden = false;
}

async function initMapWidget(mapWidget) {
  const data = await loadData(mapWidget);
  const badgeMapping = await loadBadgeMapping(mapWidget);
  const brokenSeals = await preloadBadgeImages(badgeMapping);

  const mapElement = createElement('div', 'map-widget__map');
  mapWidget.appendChild(mapElement);

  const mapSvg = createMapSvg(mapElement);

  mapSvg.setAttribute('viewBox', `0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`);

  const urls = getDataAttributeUrlList(mapWidget, 'geojsonUrls');
  const features = await loadGeoJsonFeatures(urls);

  const d3PathGenerator = createD3ProjectionAndPathGenerator(
    VIEWBOX_WIDTH,
    VIEWBOX_HEIGHT,
    features
  );

  const mapConfig = getMapConfig(mapWidget);
  const infoPanelConfig = getInfoPanelConfig(mapWidget);
  const panel = buildInfoPanel(mapWidget);

  let tooltip = null;
  if (mapConfig.showTooltip) {
    tooltip = createTooltip(mapElement);
  }

  // Categories power both the (optional) category bar and the (optional) summary
  // view, so collect them when either is enabled and the data has any.
  let categories = null;
  if (mapConfig.showCategoryBar || mapConfig.showSummary) {
    const found = collectCategories(data);
    if (found.length) {
      categories = found;
    }
  }

  let categoryBar = null;
  if (mapConfig.showCategoryBar && categories) {
    categoryBar = createCategoryBar(mapElement, mapConfig);
  }

  const context = {
    panel: panel,
    data: data,
    mapConfig: mapConfig,
    infoPanelConfig: infoPanelConfig,
    badgeMapping: badgeMapping,
    brokenSeals: brokenSeals,
    badgeCache: {},
    active: null,
    focusables: [],
    tooltip: tooltip,
    categories: categories,
    categoryBar: categoryBar
  };

  //    Paint the panel's initial default view (summary or placeholder).
  setupDefaultView(context);

  // Accessibility: Escape provides a keyboard exit without moving the pointer.
  // The first press dismisses the hover tooltip (if it's showing); once the
  // tooltip is hidden, a further press clears the active (hovered/selected)
  // feature, returning the map to its placeholder state.
  document.addEventListener('keydown', keyEvent => {
    if (keyEvent.key !== 'Escape') {
      return;
    }

    if (context.tooltip && !context.tooltip.hidden) {
      hideTooltip(context);
      return;
    }

    if (context.active) {
      clearActive(context);
    }
  });

  drawFeatures(mapSvg, features, d3PathGenerator, context);

  // Draw DC
  drawBadge(mapSvg, DC_BADGE, context);

  // Build the keyboard/screen-reader controls once every feature (and the DC
  // badge) has registered itself on context.focusables.
  buildAccessibleControls(mapElement, context);
}

function initAllMapWidgets() {
  const mapWidgets = document.querySelectorAll('.map-widget');

  for (const mapWidget of mapWidgets) {
    initMapWidget(mapWidget).catch(error => {
      const dataSrc = mapWidget.dataset.dataSrc || '(no data-data-src set)';
      console.error(
        `MapWidget: failed to initialize. Could not load data from "${dataSrc}".`,
        error
      );
    });
  }
}

// Boot every `.map-widget` element once the DOM is ready. This lets the script
// be loaded from the <head> (before the widget markup exists) as well as from
// the end of the <body>.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAllMapWidgets);
} else {
  initAllMapWidgets();
}
