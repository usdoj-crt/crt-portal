(function() {
  'use strict';

  var widget = document.getElementById('llm-chat-widget');
  if (!widget) return;

  var toggle = document.getElementById('llm-chat-toggle');
  var panel = document.getElementById('llm-chat-panel');
  var heading = document.getElementById('llm-chat-heading');
  var closeBtn = document.getElementById('llm-chat-close');
  var messages = document.getElementById('llm-chat-messages');
  var bottomSection = document.getElementById('llm-chat-bottom');
  var resizeHandle = document.getElementById('llm-chat-resize');
  var quickActions = document.getElementById('llm-chat-quick-actions');
  var summarizeBtn = document.getElementById('llm-chat-summarize');
  var inputPanel = document.getElementById('llm-chat-input-panel');
  var input = document.getElementById('llm-chat-input');
  var sendBtn = document.getElementById('llm-chat-send');

  panel.style.minWidth = '400px';
  panel.style.minHeight = '300px';
  panel.style.height = '450px';
  heading.style.flexShrink = '0';
  bottomSection.style.flexShrink = '0';
  input.style.resize = 'none';
  input.style.maxWidth = 'none';
  input.style.maxHeight = '600px';

  resizeHandle.style.cursor = 'nw-resize';
  resizeHandle.style.transform = 'rotate(-45deg)';
  resizeHandle.addEventListener('mousedown', function(e) {
    e.preventDefault();
    var startX = e.clientX;
    var startY = e.clientY;
    var startW = panel.offsetWidth;
    var startH = panel.offsetHeight;

    function onMove(e) {
      panel.style.width = Math.max(200, startW - (e.clientX - startX)) + 'px';
      panel.style.height = Math.max(200, startH - (e.clientY - startY)) + 'px';
    }

    function onUp() {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  });

  // Detect if we're on a report detail page and expose the summarize button.
  var reportId = widget.dataset.reportId || null;
  if (reportId && quickActions) {
    quickActions.removeAttribute('hidden');
  }

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
    var messageWrapper = document.createElement('div');
    messageWrapper.className = 'display-flex margin-1'

    var div = document.createElement('div');
    // Base classes for all messages
    div.className = 'padding-1 radius-md maxw-card-lg';
    div.style.whiteSpace = 'pre-wrap';
    div.style.wordWrap = 'break-word';

    if (role === 'user') {
      div.className += ' bg-primary text-white';
      messageWrapper.className += ' flex-justify-end'
    } else if (role === 'assistant') {
      div.className += ' bg-base-lightest text-base-darkest';
      messageWrapper.className += ' flex-justify-start'
    } else if (role === 'error') {
      div.className += ' bg-error-lighter text-error-dark';
      messageWrapper.className += ' flex-justify-start'
    }

    div.textContent = text;
    messages.appendChild(messageWrapper);
    messageWrapper.appendChild(div);
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

  function summarize() {
    if (!reportId) return;
    summarizeBtn.disabled = true;
    sendBtn.disabled = true;
    addMsg('Summarize this report', 'user');
    showTyping();

    fetch('/form/view/' + reportId + '/llm/summarize/', {
      headers: { 'X-CSRFToken': getCookie('csrftoken') }
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
      summarizeBtn.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    });
  }

  sendBtn.addEventListener('click', send);

  if (summarizeBtn) {
    summarizeBtn.addEventListener('click', summarize);
  }

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });
})();
