(function(root, dom) {
  function refreshQr(container, control) {
    const qr = qrcode(0, 'H');
    size = control.value;
    const source = document.querySelector(container.dataset.qrSource);
    qr.addData(source.value);
    qr.make();
    container.querySelector('.output').innerHTML = qr.createImgTag(size);
  }

  /** Keeps track of the control counts for adding the label. */
  sizeControlCount = 0;
  function createSizeControl(container) {
    const controlContainer = document.createElement('div');
    const control = document.createElement('input');
    control.id = `qr-size-${sizeControlCount}`;
    sizeControlCount++;
    control.className = 'qr-size';
    control.type = 'range';
    control.min = 1;
    control.value = 4;
    control.max = 28;
    control.step = 1;

    const label = document.createElement('label');
    label.for = `qr-size-${sizeControlCount}`;
    label.appendChild(document.createTextNode('Size: '));

    controlContainer.appendChild(control);
    controlContainer.appendChild(label);
    container.appendChild(controlContainer);

    control.addEventListener('change', () => {
      refreshQr(container, control);
    });
    return control;
  }

  function setupQrs() {
    const qrs = document.querySelectorAll('.qrcode');
    qrs.forEach(qr => {
      const control = createSizeControl(qr);

      const output = document.createElement('div');
      output.className = 'output';
      qr.appendChild(output);
      refreshQr(qr, control);
    });
  }

  root.addEventListener('load', setupQrs);
})(window, document);
