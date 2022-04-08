(function (root) {
  root.CRT.isUnsupportedBrowser = function () {
    return Boolean(navigator.userAgent.match(/SamsungBrowser/i));
  };
})(window, document);
