(function(root, dom) {
  function urlify(source, destination) {
    const base = destination.dataset.urlifyBase;
    const prefix = destination.dataset.urlifyPrefix;
    const encodedName = encodeURIComponent(source.value);
    const target = `/link/urlify/${prefix}?name=${encodedName}`;
    return window.fetch(target).then(response => {
      if (!response.ok) return;
      response.json().then(json => {
        if (!json.url) {
          destination.setAttribute('href', '#');
          destination.textContent = '(Unable to preview link)';
          return;
        }

        destination.setAttribute('href', `${base}${json.url}`);
        destination.textContent = `${base}${json.url}`;
      });
    });
  }

  function init() {
    const sources = Array.from(dom.querySelectorAll('[data-urlify-source]'));
    const destinations = Array.from(dom.querySelectorAll('[data-urlify-destination]'));

    const pairs = sources.map(source => {
      const name = source.dataset.urlifySource;
      const destination = destinations.find(
        destination => destination.dataset.urlifyDestination === name
      );
      if (!destination) return [source, null];
      return [source, destination];
    }, {});

    pairs.forEach(([source, destination]) => {
      if (!destination) return;
      let currentPromise = Promise.resolve();
      source.addEventListener('input', () => {
        currentPromise = currentPromise.then(() => urlify(source, destination));
      });
    });
  }
  window.addEventListener('DOMContentLoaded', init);
})(window, document);
