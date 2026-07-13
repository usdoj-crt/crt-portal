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

// Create a DOM element with an optional class name.
function createElement(tag, className) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  return node;
}

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

// Create the SVG element the map will be drawn into.
function createMapSvg(mapElement) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', 'map-widget__svg');
  mapElement.appendChild(svg);
  return svg;
}

function getMapConfig(mapWidget) {
  const mapConfig = {};

  mapConfig.defaultFillColor = mapWidget?.dataset?.mapDefaultFillColor || '#3498db';

  mapConfig.activeFillColor = mapWidget?.dataset?.mapActiveFillColor || '#f4c430';

  mapConfig.strokeColor = mapWidget?.dataset?.mapStrokeColor || '#ffffff';

  mapConfig.strokeWidth = mapWidget?.dataset?.mapStrokeWidth || '1';

  mapConfig.badgeTextColor = mapWidget?.dataset?.mapBadgeTextColor || '#ffffff';

  mapConfig.badgeRadius = mapWidget?.dataset?.mapBadgeRadius || '16';

  return mapConfig;
}

function getInfoPanelConfig(mapWidget) {
  const infoPanelConfig = {};

  infoPanelConfig.placeholderText = mapWidget?.dataset?.infoPanelPlaceholderText || '';

  infoPanelConfig.headingClasses = mapWidget?.dataset?.infoPanelHeadingClasses || '';

  infoPanelConfig.subheadingClasses = mapWidget?.dataset?.infoPanelSubheadingClasses || '';

  infoPanelConfig.listClasses = mapWidget?.dataset?.infoPanelListClasses || '';

  infoPanelConfig.listItemClasses = mapWidget?.dataset?.infoPanelListItemClasses || '';

  infoPanelConfig.noDataText = mapWidget?.dataset?.infoPanelNoDataText || '';

  infoPanelConfig.noDataParagraphClasses =
    mapWidget?.dataset?.infoPanelNoDataParagraphClasses || '';

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
async function loadData(mapWidget) {
  const url = mapWidget.dataset.dataSrc;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load data "${url}" (HTTP ${response.status})`);
  }
  return await response.json();
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

  context.active = { shape: shape, feature: feature };
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

    path.addEventListener('mouseover', () => {
      setActive(context, path, feature);
    });

    path.addEventListener('click', () => {
      setActive(context, path, feature);
    });

    mapSvg.appendChild(path);
    hideActive(path, context.mapConfig);
  }
}

function drawBadge(mapSvg, badge, context) {
  // 1. Create a <g> group so the circle + label share listeners.
  const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  group.setAttribute('class', 'map-widget__badge');

  // 2. Create the circle. Set cx, cy, r attributes from `badge`.
  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', badge.cx);
  circle.setAttribute('cy', badge.cy);
  circle.setAttribute('r', parseInt(context.mapConfig?.badgeRadius || 16)); // TODO Make me configurable
  circle.style.stroke = context.mapConfig?.strokeColor || '#ffffff';
  circle.style.strokeWidth = context.mapConfig?.strokeWidth || '2';
  group.appendChild(circle);

  // 3. Create the text label, centered on the circle.
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', badge.cx);
  text.setAttribute('y', badge.cy);
  text.setAttribute('text-anchor', 'middle');
  text.setAttribute('dominant-baseline', 'central');
  text.style.fill = context.mapConfig?.badgeTextColor || '#ffffff';
  text.textContent = badge.label;
  group.appendChild(text);

  // 4. Build the synthetic feature renderInfo expects.
  const feature = {
    properties: { code: badge.code, name: badge.name }
  };

  // 5. Wire the listeners as a state. On hover/click the badge becomes the
  //    single active shape and stays active after the pointer leaves.
  //    Note: pass `circle` (not the group) to setActive/hideActive,
  //    since .style.fill needs to land on the shape.
  group.addEventListener('mouseover', () => {
    setActive(context, circle, feature);
  });

  group.addEventListener('click', () => {
    setActive(context, circle, feature);
  });

  // 6. Append the group to the svg, then set the resting fill.
  mapSvg.appendChild(group);
  hideActive(circle, context.mapConfig);
}

function buildInfoPanel(mapWidget, infoPanelConfig) {
  const panel = createElement('div', 'map-widget__panel');
  mapWidget.appendChild(panel);

  renderInfoPlaceholder(panel, infoPanelConfig);

  return panel;
}

function renderInfoPlaceholder(panel, infoPanelConfig) {
  panel.innerHTML = infoPanelConfig.placeholderText || '';
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

function renderInfo(context, feature) {
  const { panel, data, infoPanelConfig } = context;

  //    Resolve the state's code from the hovered/clicked feature and look up
  //    its matching record in the loaded data set.
  const stateCode = feature.properties.code;
  const stateData = data[stateCode];

  //    Clear whatever was in the panel (placeholder or a previous state).
  panel.innerHTML = '';

  //    Build a flex container so the state badge and heading sit side by side.
  const headingContainer = createElement('div', 'map-widget__heading-container');

  //    Add the heading with the full state name, preferring the data set's
  //    name and falling back to the feature's own name.
  const heading = createElement('h2');
  heading.textContent = stateData?.name ?? feature.properties.name;
  if (infoPanelConfig?.headingClasses) {
    heading.className = infoPanelConfig.headingClasses;
  }
  headingContainer.appendChild(heading);

  //    Add the small pill badge showing the state's abbreviation (e.g. "CA").
  const stateBadge = createElement('span', 'map-widget__state-badge');
  stateBadge.textContent = stateCode;
  headingContainer.appendChild(stateBadge);

  //    Add the heading row into the panel.
  panel.appendChild(headingContainer);

  //    Add the short accent bar shown beneath the heading.
  const separator = createElement('div', 'map-widget__separator');
  panel.appendChild(separator);

  //    If the state has no actions, show the "no data" message and stop here.
  const actionsList = stateData?.actions ?? [];
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
    text.textContent = action.action;
    content.appendChild(text);

    // 10f. Add a formatted date when one is present.
    if (action.date !== null) {
      const date = createElement('div', 'map-widget__action-date');
      date.textContent = formatActionDate(action.date);
      content.appendChild(date);
    }

    // 10g. Assemble the row and append the finished item to the list.
    row.appendChild(content);

    item.appendChild(row);

    list.appendChild(item);
  }

  // 11. Append the fully built actions list to the panel.
  panel.appendChild(list);
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
  const panel = buildInfoPanel(mapWidget, infoPanelConfig);

  const context = {
    panel: panel,
    data: data,
    mapConfig: mapConfig,
    infoPanelConfig: infoPanelConfig,
    badgeMapping: badgeMapping,
    brokenSeals: brokenSeals,
    badgeCache: {},
    active: null
  };

  drawFeatures(mapSvg, features, d3PathGenerator, context);

  // Draw DC
  drawBadge(mapSvg, DC_BADGE, context);
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
