// USA Map Widget (d3-geo) — block-driven info panel.
//
// This is a standalone map widget. It shares the same US map engine as the
// legacy widget (d3 projection, GeoJSON drawing, hover/click/focus
// interactions, tooltip, and keyboard/screen-reader controls), but the info
// panel is rendered from a generic BLOCK vocabulary described by the map's JSON
// data, rather than a fixed hardcoded shape.
//
// The design goal: the DISPLAY and STRUCTURE of every panel come from the JSON.
// New kinds of maps and data displays can be authored (as MapWidgetData records)
// without touching this file.
//
// Data shape:
//   {
//     "features": {
//       "AZ": {                       // keyed by state code (joins to the map)
//         "name": "Arizona",          // used by the tooltip + a11y controls
//         "url": "...",               // optional; opened on click
//         "display": {                 // named surfaces (see below)
//           "panel":       [ ...blocks... ],  // rendered beside the map
//           "categoryBar": { ...config... }   // rendered beneath the map (opt.)
//         }
//       }
//     },
//     "default": {                     // shown when nothing is selected
//       "name": "Nationwide",         // optional; used by the tooltip + a11y
//       "badge": "USA",               // optional
//       "display": { "panel": [ ...blocks... ] }
//     }
//   }
//
// `display` is an OBJECT of named SURFACES. Two surfaces exist, and they are
// DIFFERENT KINDS of thing:
//   - `panel`:       a list of generic BLOCKS (the composable vocabulary below),
//                    rendered in the details region beside the map. Always shown.
//   - `categoryBar`: a specific COMPONENT (not blocks) with its own fixed schema,
//                    rendered as a strip beneath the map. Only shown when the
//                    widget has `data-map-show-bar="true"` AND the record
//                    supplies a `categoryBar`. When either is absent the bar
//                    element stays hidden (and, on the election-integrity page,
//                    CSS also hides it on mobile). The default/placeholder views
//                    never show the bar. See renderCategoryBar() for its schema.
//
// The `panel` surface is built from an ordered list of BLOCKS. This is a small,
// CLOSED, semantic vocabulary — not arbitrary HTML. The widget owns the
// markup/CSS; the data only says WHAT to show, never HOW. An unknown block type
// is skipped silently. Adding a block type is a deliberate code change here, not
// a data feature. Keeping this set small is what keeps the widget generic and
// safe (the emitted HTML is an allowlist by construction).
//
// Every value in a block is a plain literal (string/number). The widget performs
// NO computation. If totals/counts need deriving, that happens upstream (e.g. a
// Django transform that generates `display`) — never in this file.
//
// Blocks (all leaves — there is no generic container; the one horizontal
// pattern, the category breakdown, is its own `lineItem` block below):
//     { "type": "heading", "value": "Arizona", "badge": "AZ" }  // panel title
//     { "type": "separator" }                                    // divider rule
//     { "type": "subheading", "value": "Latest Actions" }        // section label
//     { "type": "note", "value": "Hover a state..." }            // prose <p>
//     { "type": "stat", "value": 32, "label": "counties monitored" }
//     { "type": "stat", "icon": "cybersecurity", "value": 6,
//         "label": "Cybersecurity" }   // icon = a sprite symbol slug (renders
//                                       // <use href="#icon-cybersecurity">, uses
//                                       // currentColor)
//     { "type": "lineItem", "icon": "cybersecurity", "label": "Cybersecurity",
//         "value": 300 }               // icon + label at left, value at right,
//                                       // hairline rules above/below (the legacy
//                                       // Nationwide category breakdown)
//     { "type": "list", "items": [
//         { "bullet": { "image": "static:img/seal.svg", "label": "Civil" },
//           "date": "Sep 18, 2026",
//           "label": "DOJ ensures military ballots sent early" }
//     ]}
//   The bullet's `image` (a resolved URL) renders as the leading icon; if it's
//   absent or fails to load, the bullet `label` is shown as a text pill instead.
//

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

// ---------------------------------------------------------------------------
// Small DOM/utility helpers
// ---------------------------------------------------------------------------

// Create a DOM element with an optional class name.
function createElement(tag, className) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  return node;
}

// Create the SVG element the map will be drawn into.
function createMapSvg(mapElement) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', 'usa-map-widget__svg');

  // Hide the map from screen readers. SVGs are not reliably accessible so we
  // provide a separate set of keyboard/screen-reader controls that fully
  // replicate the map's interactivity (see buildAccessibleControls).
  svg.setAttribute('aria-hidden', 'true');
  mapElement.appendChild(svg);
  return svg;
}

// Read a comma-separated list from a data attribute; [] if missing.
function getDataAttributeUrlList(mapWidget, attributeName) {
  const value = mapWidget.dataset[attributeName] || '';
  if (value === '') {
    return [];
  }
  return value.split(',');
}

// ---------------------------------------------------------------------------
// Map configuration (from the widget element's data-* attributes)
//
// The USA map widget's config is deliberately small: it configures the MAP
// (colors, tooltip), not the panel. All panel styling/structure comes from the
// JSON blocks + CSS.
// ---------------------------------------------------------------------------

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
  mapConfig.showBar = mapWidget?.dataset?.mapShowBar === 'true';

  return mapConfig;
}

// ---------------------------------------------------------------------------
// Data + GeoJSON loading
// ---------------------------------------------------------------------------

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
// an empty object so the map still renders, with every feature showing its
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

// ---------------------------------------------------------------------------
// Tooltip (follows the cursor while hovering a feature)
// ---------------------------------------------------------------------------

// The tooltip is absolutely positioned within the map area, and its coordinates
// are measured relative to the map area, so it's appended inside
// `.usa-map-widget__map`.
function createTooltip(mapElement) {
  const tooltip = createElement('div', 'usa-map-widget__tooltip');
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
  const name = context.features?.[code]?.name ?? feature.properties.name;

  tooltip.innerHTML = '';

  const tooltipName = createElement('span', 'usa-map-widget__tooltip-name');
  tooltipName.textContent = name;
  tooltip.appendChild(tooltipName);

  const tooltipBadge = createElement('span', 'usa-map-widget__pill');
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

  // Flip thresholds are measured against the SVG (the actual map area), not the
  // whole map card. The card can be taller than the SVG when the summary bar is
  // rendered below it; without this the tooltip would only flip at the bottom of
  // the bar instead of the bottom of the map. The tooltip is still positioned in
  // the card's coordinate space (it's absolutely positioned within mapElement),
  // and the SVG sits flush at the card's top-left, so widths/heights line up.
  const mapArea = mapElement.querySelector('.usa-map-widget__svg');
  const areaBounds = mapArea ? mapArea.getBoundingClientRect() : bounds;

  // If a right-side tooltip would overflow the map's right edge, flip it to the
  // left of the cursor so it stays within the (overflow-clipped) map area.
  const overflowsRight = x + TOOLTIP_OFFSET + tooltip.offsetWidth > areaBounds.width;
  const left = overflowsRight ? x - TOOLTIP_OFFSET - tooltip.offsetWidth : x + TOOLTIP_OFFSET;

  // Likewise flip above the cursor when we would overflow the bottom edge.
  const overflowsBottom = y + TOOLTIP_OFFSET + tooltip.offsetHeight > areaBounds.height;
  const top = overflowsBottom ? y - TOOLTIP_OFFSET - tooltip.offsetHeight : y + TOOLTIP_OFFSET;

  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
}

function hideTooltip(context) {
  if (context.tooltip) {
    context.tooltip.hidden = true;
  }
}

// ---------------------------------------------------------------------------
// Active-feature state (the hovered/selected shape)
// ---------------------------------------------------------------------------

function showActive(path, mapConfig) {
  path.style.fill = mapConfig?.activeFillColor || '#f4c430';
}

function hideActive(path, mapConfig) {
  path.style.fill = mapConfig?.defaultFillColor || '#3498db';
}

// Make `shape` the single active shape: restore the previously active shape (if
// any) to its resting state, highlight the new one, render its info panel, and
// record it on the context so it stays active after the pointer leaves.
function setActive(context, shape, feature) {
  if (context.active && context.active.shape !== shape) {
    hideActive(context.active.shape, context.mapConfig);
  }

  showActive(shape, context.mapConfig);
  renderFeatureView(context, feature);

  context.active = { shape: shape, feature: feature };
}

// Clear the active (hovered/selected) feature: reset its fill, drop the active
// reference, and restore the panel's default view. Returns the widget to its
// initial "nothing selected" state.
function clearActive(context) {
  if (context.active) {
    hideActive(context.active.shape, context.mapConfig);
    context.active = null;
  }

  renderDefaultView(context);
}

// Navigate to the URL associated with a feature (from the loaded data set).
// Opens in a new tab when the open_in_new_tab option is set, otherwise in the
// current tab (the accessible default). Used by pointer clicks and keyboard/
// screen-reader activation. Hover and focus intentionally do NOT call this —
// they only highlight via setActive().
function openFeatureUrl(context, feature) {
  const stateCode = feature.properties.code;
  const url = context.features?.[stateCode]?.url;

  if (url) {
    if (context.mapConfig?.openInNewTab) {
      window.open(url, '_blank', 'noopener');
    } else {
      window.location.assign(url);
    }
  }
}

// ---------------------------------------------------------------------------
// Drawing the map (states + the DC badge)
// ---------------------------------------------------------------------------

function drawFeatures(mapSvg, features, d3PathGenerator, context) {
  for (const feature of features) {
    const d = d3PathGenerator(feature);

    if (!d) {
      continue;
    }

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('class', 'usa-map-widget__feature');
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
  // Create a <g> group so the circle + label share listeners.
  const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  group.setAttribute('class', 'usa-map-widget__badge');

  // Create the circle. Set cx, cy, r attributes from `badge`.
  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', badge.cx);
  circle.setAttribute('cy', badge.cy);
  circle.setAttribute('r', parseInt(context.mapConfig?.badgeRadius || 16));
  circle.style.stroke = context.mapConfig?.strokeColor || '#ffffff';
  circle.style.strokeWidth = context.mapConfig?.strokeWidth || '2';
  group.appendChild(circle);

  // Create the text label, centered on the circle.
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', badge.cx);
  text.setAttribute('y', badge.cy);
  text.setAttribute('text-anchor', 'middle');
  text.setAttribute('dominant-baseline', 'central');
  text.style.fill = context.mapConfig?.badgeTextColor || '#ffffff';
  text.textContent = badge.label;
  group.appendChild(text);

  // Build the synthetic feature the panel renderer expects.
  const feature = {
    properties: { code: badge.code, name: badge.name }
  };

  // Wire the listeners as a state. On hover/click the badge becomes the single
  // active shape and stays active after the pointer leaves. Note: pass `circle`
  // (not the group) to setActive/hideActive, since .style.fill needs to land on
  // the shape.
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

  // Append the group to the svg, then set the resting fill.
  mapSvg.appendChild(group);
  hideActive(circle, context.mapConfig);

  // Register the badge alongside the map features so it gets a matching
  // keyboard/screen-reader control (see buildAccessibleControls()).
  context.focusables.push({
    name: badge.name,
    feature: feature,
    shape: circle
  });
}

// ---------------------------------------------------------------------------
// Info panel container + default-view plumbing
// ---------------------------------------------------------------------------

function buildInfoPanel(mapWidget) {
  const panel = createElement('div', 'usa-map-widget__panel');

  panel.setAttribute('role', 'region');
  panel.setAttribute('aria-label', 'Selected state details');

  // The panel content can get long, so we set assertive here to ensure we
  // interrupt when the user changes features.
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
  // 2-in-1 switching between touchscreen and trackpad), so any hover-dependent
  // guidance stays correct.
  if (typeof window.matchMedia === 'function') {
    const hoverQuery = window.matchMedia('(hover: hover)');
    hoverQuery.addEventListener('change', () => {
      // Only re-render while no feature is selected; don't clobber a
      // selected feature's details.
      if (!context.active) {
        renderDefaultView(context);
      }
    });
  }
}

// ---------------------------------------------------------------------------
// Info Bar
// ---------------------------------------------------------------------------

function buildBar(parent) {
  const bar = createElement('div', 'usa-map-widget__bar');

  bar.setAttribute('role', 'region');
  bar.setAttribute('aria-label', 'Summary statistics');
  bar.setAttribute('aria-live', 'polite');
  bar.setAttribute('aria-atomic', 'true');

  // Hidden until a record with bar content renders
  bar.hidden = true;

  parent.appendChild(bar);

  return bar;
}

function showBar(context) {
  if (context.bar) {
    context.bar.hidden = false;
  }
}

function hideBar(context) {
  if (context.bar) {
    context.bar.hidden = true;
    context.bar.innerHTML = '';
  }
}

// Render the category-bar COMPONENT into the bar surface. This is deliberately
// NOT a block: the category bar is a specific, fixed-structure component (a
// caption + optional total in a header, then a strip of category slots), so it
// has its own schema and its own renderer rather than being composed from
// generic blocks. Config shape:
//   {
//     "caption": "enforcement actions by type",   // suffix after the state name
//     "total":   { "value": 13, "label": "Total" },   // optional
//     "slots":   [ { "icon": "cybersecurity", "value": 6,
//                    "label": "Cybersecurity" }, ... ]
//   }
// The caption is prefixed with the record's `name` (e.g. "Alaska"), rendered in
// gold — the state name isn't re-authored here since the record already has it.
// `icon` on a slot is a sprite symbol slug (see the icon sprite template). A
// slot whose value is 0 is marked "empty" so CSS can dim it.
function renderCategoryBar(context, record, config) {
  context.bar.innerHTML = '';

  // Header: caption on the left, optional total on the right.
  const header = createElement('div', 'usa-map-widget__category-bar-header');

  const caption = createElement('span', 'usa-map-widget__category-bar-caption');

  // Gold state-name prefix, taken from the record (not re-authored in config),
  // kept as its own span so it can be colored independently of the rest.
  if (record?.name) {
    const state = createElement('span', 'usa-map-widget__category-bar-caption-state');
    state.textContent = record.name;
    caption.appendChild(state);
  }

  if (config.caption) {
    const text = createElement('span', 'usa-map-widget__category-bar-caption-text');
    text.textContent = config.caption;
    caption.appendChild(text);
  }

  header.appendChild(caption);

  if (config.total) {
    const total = createElement('span', 'usa-map-widget__category-bar-total');

    const count = createElement('span', 'usa-map-widget__category-bar-total-count');
    count.textContent = config.total.value ?? '';
    total.appendChild(count);

    const label = createElement('span', 'usa-map-widget__category-bar-total-label');
    label.textContent = config.total.label ?? '';
    total.appendChild(label);

    header.appendChild(total);
  }

  context.bar.appendChild(header);

  // Slots strip: one column per category.
  const slots = createElement('div', 'usa-map-widget__category-bar-slots');

  for (const slot of config.slots ?? []) {
    const slotEl = createElement('div', 'usa-map-widget__category-bar-slot');
    if (slot.value === 0) {
      slotEl.classList.add('usa-map-widget__category-bar-slot--empty');
    }

    const top = createElement('div', 'usa-map-widget__category-bar-slot-top');
    if (slot.icon) {
      top.appendChild(createIconSvg(slot.icon, 'usa-map-widget__category-bar-slot-icon'));
    }
    const count = createElement('span', 'usa-map-widget__category-bar-slot-count');
    count.textContent = slot.value ?? '';
    top.appendChild(count);
    slotEl.appendChild(top);

    const label = createElement('span', 'usa-map-widget__category-bar-slot-label');
    label.textContent = slot.label ?? '';
    slotEl.appendChild(label);

    slots.appendChild(slotEl);
  }

  context.bar.appendChild(slots);
}

// ---------------------------------------------------------------------------
// Accessibility: keyboard/screen-reader controls
// ---------------------------------------------------------------------------

// Build a visually hidden, keyboard-focusable control for every mapped feature
// so the map is fully operable without a pointer. Native <button>s are used so
// they join the natural tab order. Controls are appended alphabetically by
// feature name. Activating a control makes its feature active — the map
// highlights and the info panel renders exactly as it does on hover.
function buildAccessibleControls(mapElement, context) {
  const controls = createElement('div', 'usa-map-widget__sr-controls');
  controls.setAttribute('role', 'group');
  controls.setAttribute('aria-label', 'Select a state to view its details');

  const sorted = context.focusables.slice().sort((a, b) => a.name.localeCompare(b.name));

  for (const entry of sorted) {
    const button = createElement('button', 'usa-map-widget__sr-control');
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

// ===========================================================================
// BLOCK READER / INFO-PANEL RENDERER
//
// Everything ABOVE this line is the shared map engine + plumbing. Everything
// BELOW it reads the JSON blocks and renders the info panel. We build this out
// incrementally, one block type at a time.
//
// This is the real info-panel renderer. It reads a record's `display` list and
// renders each block into the panel. Dispatch is a switch in renderBlock(); each
// block type has its own render function. Unknown types are skipped silently.
// New block types are added here (a switch case + a render function).
// ===========================================================================

// heading block: the panel's title — the region name plus an optional pill
// badge (e.g. a state abbreviation).
function renderHeading(context, record, block, target) {
  const heading = createElement('div', 'usa-map-widget__heading');

  const title = createElement('h3', 'usa-map-widget__heading-title');
  title.textContent = block.value ?? '';
  heading.appendChild(title);

  if (block.badge) {
    const badge = createElement('span', 'usa-map-widget__pill');
    badge.textContent = block.badge;
    heading.appendChild(badge);
  }

  target.appendChild(heading);
}

// separator block: a short decorative accent bar dividing sections.
function renderSeparator(context, record, block, target) {
  const separator = createElement('div', 'usa-map-widget__separator');
  target.appendChild(separator);
}

// subheading block: a small label introducing a section within the panel.
function renderSubheading(context, record, block, target) {
  const subheading = createElement('h4', 'usa-map-widget__subheading');
  subheading.textContent = block.value ?? '';
  target.appendChild(subheading);
}

// note block: a plain prose paragraph (also used for the placeholder message).
function renderNote(context, record, block, target) {
  const note = createElement('p', 'usa-map-widget__note');
  note.textContent = block.value ?? '';
  target.appendChild(note);
}

// Build an inline SVG icon that references a symbol in the page's icon sprite
// (see usa_map_widget_icon_sprite.html). Renders <svg><use href="#icon-<slug>">;
// it uses `currentColor`, so its color follows the surrounding text. Shared by
// the stat block and the category-bar component.
function createIconSvg(slug, className) {
  const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  icon.setAttribute('class', className);
  icon.setAttribute('aria-hidden', 'true');

  const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
  use.setAttribute('href', `#icon-${slug}`);
  icon.appendChild(use);

  return icon;
}

// stat block: a prominent value paired with a descriptive label
// (e.g. "32 counties monitored"), with an optional leading icon (a sprite slug).
function renderStat(context, record, block, target) {
  const stat = createElement('div', 'usa-map-widget__stat');

  // Top line: optional icon next to the value.
  const top = createElement('div', 'usa-map-widget__stat-top');

  if (block.icon) {
    top.appendChild(createIconSvg(block.icon, 'usa-map-widget__stat-icon'));
  }

  const value = createElement('span', 'usa-map-widget__stat-value');
  value.textContent = block.value ?? '';
  top.appendChild(value);

  stat.appendChild(top);

  const label = createElement('span', 'usa-map-widget__stat-label');
  label.textContent = block.label ?? '';
  stat.appendChild(label);

  target.appendChild(stat);
}

// Build the text-pill fallback used when a list item's bullet has no image
// (or its image fails to load). Shows the bullet's label.
function createBulletPill(label) {
  const pill = createElement('span', 'usa-map-widget__bullet-pill');
  pill.textContent = label ?? '';
  return pill;
}

// Build a list item's leading bullet: the bullet image when present (falling
// back to a text pill if it fails to load), a text pill when there's only a
// label, or nothing when the bullet has neither image nor label.
function createBullet(bullet) {
  const image = bullet?.image;
  const label = bullet?.label ?? '';

  if (!image && !label) {
    return null;
  }

  // No image → text pill straight away.
  if (!image) {
    return createBulletPill(label);
  }

  // Image present → use it, but fall back to the pill if it fails to load.
  const img = createElement('img', 'usa-map-widget__bullet-image');
  img.src = image;
  img.alt = label;
  img.addEventListener('error', () => {
    img.replaceWith(createBulletPill(label));
  });
  return img;
}

// list block: a vertical list of items, each with an optional leading bullet,
// an optional date eyebrow, and a label.
function renderList(context, record, block, target) {
  const items = block.items ?? [];
  const list = createElement('ul', 'usa-map-widget__list');

  for (const item of items) {
    const li = createElement('li', 'usa-map-widget__list-item');

    const bullet = createBullet(item.bullet);
    if (bullet) {
      li.appendChild(bullet);
    }

    const content = createElement('div', 'usa-map-widget__list-content');

    if (item.date) {
      const date = createElement('span', 'usa-map-widget__list-date');
      date.textContent = item.date;
      content.appendChild(date);
    }

    const label = createElement('span', 'usa-map-widget__list-label');
    label.textContent = item.label ?? '';
    content.appendChild(label);

    li.appendChild(content);

    list.appendChild(li);
  }

  target.appendChild(list);
}

// lineItem block: a single labelled line with an optional leading icon (a sprite
// slug) and a trailing value, separated by a flexible gap so the value sits at
// the far right (e.g. "[icon] Cybersecurity ....... 300"). Hairline rules above
// and below come from CSS. This is the legacy Nationwide category-breakdown row.
function renderLineItem(context, record, block, target) {
  const item = createElement('div', 'usa-map-widget__line-item');

  // Left cluster: optional icon + label, kept together.
  const left = createElement('div', 'usa-map-widget__line-item-left');

  if (block.icon) {
    left.appendChild(createIconSvg(block.icon, 'usa-map-widget__line-item-icon'));
  }

  const label = createElement('span', 'usa-map-widget__line-item-label');
  label.textContent = block.label ?? '';
  left.appendChild(label);

  item.appendChild(left);

  const value = createElement('span', 'usa-map-widget__line-item-value');
  value.textContent = block.value ?? '';
  item.appendChild(value);

  target.appendChild(item);
}

// Render the panel's placeholder view — shown when there's nothing to display
// (a hovered feature with no record, or no default record when idle).
function renderPlaceholder(context) {
  context.panel.innerHTML = '';
  renderNote(context, null, { value: 'Select a state to see details.' }, context.panel);
  hideBar(context);
}

function renderBlock(context, record, block, target) {
  switch (block?.type) {
    case 'heading':
      renderHeading(context, record, block, target);
      break;
    case 'separator':
      renderSeparator(context, record, block, target);
      break;
    case 'subheading':
      renderSubheading(context, record, block, target);
      break;
    case 'note':
      renderNote(context, record, block, target);
      break;
    case 'stat':
      renderStat(context, record, block, target);
      break;
    case 'list':
      renderList(context, record, block, target);
      break;
    case 'lineItem':
      renderLineItem(context, record, block, target);
      break;
    default:
      // unknown/missing type — skip silently
      break;
  }
}

function renderBlocks(context, record, blocks, parent) {
  for (const block of blocks) {
    renderBlock(context, record, block, parent);
  }
}

// Render a region's record into its display surfaces: the `panel` (always, from
// generic blocks) and, when the widget has a bar and the record supplies a
// `categoryBar` config, the category-bar component. A record with no categoryBar
// (e.g. the default/Nationwide view) leaves the bar hidden.
function renderRecord(context, record) {
  const display = record?.display ?? {};

  context.panel.innerHTML = '';
  renderBlocks(context, record, display.panel ?? [], context.panel);

  if (context.bar) {
    if (display.categoryBar) {
      renderCategoryBar(context, record, display.categoryBar);
      showBar(context);
    } else {
      hideBar(context);
    }
  }
}

// Render the panel for a hovered/selected feature. Falls back to the
// placeholder view when the feature has no record (nothing to display).
function renderFeatureView(context, feature) {
  const code = feature.properties.code;
  const record = context.features[code];

  if (!record) {
    renderPlaceholder(context);
    return;
  }

  renderRecord(context, record);
}

// Render the panel for the default feature
function renderDefaultView(context) {
  if (context.defaultRecord) {
    renderRecord(context, context.defaultRecord); // path 2
  } else {
    renderPlaceholder(context); // path 3
  }
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

async function initMapWidget(mapWidget) {
  const loaded = await loadData(mapWidget);
  const features = loaded.features || {};

  const mapElement = createElement('div', 'usa-map-widget__map');
  mapWidget.appendChild(mapElement);

  const mapSvg = createMapSvg(mapElement);
  mapSvg.setAttribute('viewBox', `0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`);

  const urls = getDataAttributeUrlList(mapWidget, 'geojsonUrls');
  const geoFeatures = await loadGeoJsonFeatures(urls);

  const d3PathGenerator = createD3ProjectionAndPathGenerator(
    VIEWBOX_WIDTH,
    VIEWBOX_HEIGHT,
    geoFeatures
  );

  const mapConfig = getMapConfig(mapWidget);
  const panel = buildInfoPanel(mapWidget);

  let bar = null;
  if (mapConfig.showBar) {
    // Append inside the map card (below the SVG) so the bar is map-width and its
    // position is independent of the info panel's height, matching the legacy
    // widget.
    bar = buildBar(mapElement);
  }

  let tooltip = null;
  if (mapConfig.showTooltip) {
    tooltip = createTooltip(mapElement);
  }

  const context = {
    panel: panel,
    bar: bar,
    features: features,
    defaultRecord: loaded.default,
    mapConfig: mapConfig,
    active: null,
    focusables: [],
    tooltip: tooltip
  };

  // Paint the panel's initial default view.
  setupDefaultView(context);

  // Accessibility: Escape provides a keyboard exit without moving the pointer.
  // The first press dismisses the hover tooltip (if it's showing); once the
  // tooltip is hidden, a further press clears the active feature, returning the
  // map to its default state.
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

  drawFeatures(mapSvg, geoFeatures, d3PathGenerator, context);

  // Draw DC.
  drawBadge(mapSvg, DC_BADGE, context);

  // Build the keyboard/screen-reader controls once every feature (and the DC
  // badge) has registered itself on context.focusables.
  buildAccessibleControls(mapElement, context);

  // Signal that this map has finished loading (used e.g. to hide a loading
  // indicator on the page).
  mapWidget.dataset.loaded = 'true';
  mapWidget.dispatchEvent(new CustomEvent('map-widget:loaded', { bubbles: true }));
}

function initAllMapWidgets() {
  const mapWidgets = document.querySelectorAll('.usa-map-widget');

  for (const mapWidget of mapWidgets) {
    initMapWidget(mapWidget).catch(error => {
      const dataSrc = mapWidget.dataset.dataSrc || '(no data-data-src set)';
      console.error(
        `USA Map Widget: failed to initialize. Could not load data from "${dataSrc}".`,
        error
      );
    });
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAllMapWidgets);
} else {
  initAllMapWidgets();
}
