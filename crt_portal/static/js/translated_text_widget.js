(function(root, dom) {
  nextAreaId = 0;
  function createLanguageTextArea(languageCode, widget) {
    const container = document.createElement('div');
    container.className = `translated-text-part ${languageCode}`;
    const areaId = `translated-textarea-${nextAreaId}`;
    nextAreaId++;

    const textarea = document.createElement('textarea');
    textarea.className = 'vLargeTextField';
    textarea.value = getFullData(widget)[languageCode];
    textarea.id = areaId;

    const label = document.createElement('label');
    label.className = 'vLargeTextField';
    label.setAttribute('for', areaId);
    label.innerText = `For language ${languageCode}:`;

    container.appendChild(label);
    container.appendChild(textarea);

    textarea.onchange = () => {
      const fullData = getFullData(widget);
      fullData[languageCode] = textarea.value;
      widget.value = JSON.stringify(fullData);
    };

    return container;
  }

  function getFullData(widget) {
    try {
      return JSON.parse(widget.value);
    } catch (e) {
      console.warn('Failed to parse translated value (it might be empty)', e);
      return {};
    }
  }

  function createLanguageTextAreas(widget) {
    const parent = document.createElement('div');
    parent.className = 'translated-text-parent';

    const languages = widget.dataset.languageCodes.split(',');
    const areas = languages.map(code => createLanguageTextArea(code, widget));
    areas.forEach(area => {
      parent.appendChild(area);
    });

    widget.parentNode.insertBefore(parent, widget);
    widget.style.display = 'none';
  }

  function setup() {
    const widgets = dom.querySelectorAll('.vTranslatedTextField');
    widgets.forEach(createLanguageTextAreas);
  }

  root.addEventListener('load', setup);
})(window, document);
