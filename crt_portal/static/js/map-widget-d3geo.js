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
  return await response.json();
}

function showActive(path, mapConfig) {
  path.style.fill = mapConfig?.activeFillColor || '#f4c430';
}

function hideActive(path, mapConfig) {
  path.style.fill = mapConfig?.defaultFillColor || '#3498db';
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
      renderInfo(context.panel, context.data, feature, context.infoPanelConfig);
      showActive(path, context.mapConfig);
    });

    path.addEventListener('click', () => {
      renderInfo(context.panel, context.data, feature, context.infoPanelConfig);
      showActive(path, context.mapConfig);
    });

    path.addEventListener('mouseout', () => {
      renderInfoPlaceholder(context.panel, context.infoPanelConfig);
      hideActive(path, context.mapConfig);
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

  // 5. Wire the same three listeners as a state.
  //    Note: pass `circle` (not the group) to showActive/hideActive,
  //    since .style.fill needs to land on the shape.
  group.addEventListener('mouseover', () => {
    renderInfo(context.panel, context.data, feature, context.infoPanelConfig);
    showActive(circle, context.mapConfig);
  });

  group.addEventListener('click', () => {
    renderInfo(context.panel, context.data, feature, context.infoPanelConfig);
    showActive(circle, context.mapConfig);
  });

  group.addEventListener('mouseout', () => {
    renderInfoPlaceholder(context.panel, context.infoPanelConfig);
    hideActive(circle, context.mapConfig);
  });

  // 6. Append the group to the svg, then set the resting fill.
  mapSvg.appendChild(group);
  hideActive(circle, context.mapConfig);

  console.log(`Drew Badge: ${badge.name} (${badge.code}) at ${badge.cx},${badge.cy}`);
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

function renderInfo(panel, data, feature, infoPanelConfig) {
  const stateCode = feature.properties.code;
  const stateData = data[stateCode];

  panel.innerHTML = '';

  const heading = createElement('h3');
  heading.textContent = stateData?.name ?? feature.properties.name;
  if (infoPanelConfig?.headingClasses) {
    heading.className = infoPanelConfig.headingClasses;
  }
  panel.appendChild(heading);

  const subheading = createElement('h4');
  subheading.textContent = 'Abbreviation: ' + stateCode;
  if (infoPanelConfig?.subheadingClasses) {
    subheading.className = infoPanelConfig.subheadingClasses;
  }
  panel.appendChild(subheading);

  const bulletsList = stateData?.bullets ?? [];
  if (bulletsList?.length === 0) {
    const noDataParagraph = createElement('p');
    if (infoPanelConfig?.noDataParagraphClasses) {
      noDataParagraph.className = infoPanelConfig.noDataParagraphClasses;
    }
    noDataParagraph.textContent = infoPanelConfig?.noDataText || 'No data available';
    panel.appendChild(noDataParagraph);

    return;
  }

  const list = createElement('ul');
  if (infoPanelConfig?.listClasses) {
    list.className = infoPanelConfig.listClasses;
  }
  for (const bullet of bulletsList) {
    const item = createElement('li');
    if (infoPanelConfig?.listItemClasses) {
      item.className = infoPanelConfig.listItemClasses;
    }
    item.textContent = bullet;
    list.appendChild(item);
  }
  panel.appendChild(list);
}

async function initMapWidget(mapWidget) {
  const data = await loadData(mapWidget);

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
    infoPanelConfig: infoPanelConfig
  };

  drawFeatures(mapSvg, features, d3PathGenerator, context);

  // Draw DC
  drawBadge(mapSvg, DC_BADGE, context);
}

const mapWidgets = document.querySelectorAll('.map-widget');

for (const mapWidget of mapWidgets) {
  initMapWidget(mapWidget);
}
