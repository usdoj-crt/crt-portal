/**
 * Meant to be used with partials/message.html.
 *
 * See: https://designsystem.digital.gov/components/alert/ for tag options.
 *
 */
(function(root, dom) {
  root.CRT = root.CRT || {};

  root.CRT.showMessage = async function(container, { tag, content }) {
    const messages = container.querySelector('.messages');
    messages.querySelector('.message-content').innerText = content;
    messages.querySelector('.message-tag').classList.add(`usa-alert--${tag}`);
    messages.dataset.tag = tag;
    messages.hidden = false;
  };

  root.CRT.hideMessage = async function(container) {
    const messages = container.querySelector('.messages');
    const tag = messages.dataset.tag;
    if (tag) {
      messages.querySelector('.message-tag').classList.remove(`usa-alert--${tag}`);
      messages.removeAttribute('data-tag');
    }
    messages.querySelector('.message-content').innerText = '';
    messages.hidden = true;
  };
})(window, document);
