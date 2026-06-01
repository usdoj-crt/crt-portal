(function() {
  'use strict';

  var widget = document.getElementById('llm-chat-widget');
  if (!widget) return;

  var toggle = document.getElementById('llm-chat-toggle');
  var panel = document.getElementById('llm-chat-panel');
  var heading = document.getElementById('llm-chat-heading');
  var closeBtn = document.getElementById('llm-chat-close');
  var messages = document.getElementById('llm-chat-messages');
  var inputPanel = document.getElementById('llm-chat-input-panel');
  var input = document.getElementById('llm-chat-input');
  var sendBtn = document.getElementById('llm-chat-send');

  panel.style.direction = 'rtl';
  panel.style.resize = 'both';
  panel.style.minWidth = '200px';
  panel.style.minHeight = '200px';
  heading.style.direction = 'ltr';
  messages.style.direction = 'ltr';
  messages.style.flex = '1 1 auto';
  messages.style.minHeight = '0';
  inputPanel.style.direction = 'ltr';

  widget.removeAttribute('hidden');

  toggle.addEventListener('click', function() {
    var isHidden = panel.hasAttribute('hidden');
    if (isHidden) {
      panel.removeAttribute('hidden');
      input.focus();
    } else {
      panel.setAttribute('hidden', '');
    }
  });

  closeBtn.addEventListener('click', function() {
    panel.setAttribute('hidden', '');
  });

  function addMsg(text, role) {
    var div = document.createElement('div');
    // Base classes for all messages
    div.className = 'padding-1 padding-x-105 radius-md font-sans-xs line-height-sans-4 maxw-card-lg';
    div.style.whiteSpace = 'pre-wrap';
    div.style.wordWrap = 'break-word';

    if (role === 'user') {
      div.className += ' align-self-end bg-primary text-white';
    } else if (role === 'assistant') {
      div.className += ' align-self-start bg-base-lightest text-base-darkest';
    } else if (role === 'error') {
      div.className += ' align-self-start bg-error-lighter text-error-dark';
    }

    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function showTyping() {
    var div = document.createElement('div');
    div.className = 'align-self-start text-base font-sans-xs text-italic padding-05 padding-x-105';
    div.id = 'llm-chat-typing';
    div.textContent = 'Thinking...';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function removeTyping() {
    var el = document.getElementById('llm-chat-typing');
    if (el) el.remove();
  }

  function getCookie(name) {
    var match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  function send() {
    var text = input.value.trim();
    if (!text) return;
    addMsg(text, 'user');
    input.value = '';
    input.style.height = 'auto';
    sendBtn.disabled = true;
    showTyping();

    fetch('/form/llm/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ message: text })
    })
    .then(function(resp) {
      return resp.json().then(function(data) {
        return { ok: resp.ok, data: data };
      });
    })
    .then(function(result) {
      removeTyping();
      if (result.ok && result.data.response) {
        addMsg(result.data.response, 'assistant');
      } else {
        addMsg(result.data.error || 'Something went wrong.', 'error');
      }
    })
    .catch(function(err) {
      removeTyping();
      addMsg('Network error: ' + err.message, 'error');
    })
    .finally(function() {
      sendBtn.disabled = false;
      input.focus();
    });
  }

  sendBtn.addEventListener('click', send);

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });

  input.addEventListener('input', function() {
    input.style.height = 'auto';
    input.style.height = input.scrollHeight + 'px';
  });
})();
