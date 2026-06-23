/**
 * LLM Chat Widget
 *
 * A reusable chat bubble UI with built-in LLM API communication.
 * Contains no page-specific logic — page integrations should load this
 * first, then use window.LLMChat to wire up page-specific behavior.
 *
 * Public API (window.LLMChat):
 *   - addMsg(text, role)    — Append a message bubble ('user'|'assistant'|'error')
 *   - openPanel()           — Open the chat panel
 *   - closePanel()          — Close the chat panel
 *   - showTyping()          — Show "Thinking..." indicator
 *   - removeTyping()        — Remove the typing indicator
 *   - setWaiting(bool)      — Disable/enable the send button
 *   - chat(message)         — Send a freeform message to the LLM
 *   - summarize(recordIds)  — Summarize one or more records by ID
 */

(function () {
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
  var input = document.getElementById('llm-chat-input');
  var sendBtn = document.getElementById('llm-chat-send');

  var csrfToken = widget.dataset.csrfToken || '';
  var chatUrl = widget.dataset.chatUrl || '/api/llm/chat';
  var summarizeUrl = widget.dataset.summarizeUrl || '/api/llm/summarize';

  // ─── Panel sizing ────────────────────────────────────────────────────────────

  panel.style.minWidth = '400px';
  panel.style.minHeight = '300px';
  panel.style.height = '450px';
  heading.style.flexShrink = '0';
  bottomSection.style.flexShrink = '0';
  input.style.resize = 'none';
  input.style.maxWidth = 'none';
  input.style.maxHeight = '600px';

  // ─── Resize handle ───────────────────────────────────────────────────────────

  resizeHandle.style.cursor = 'nw-resize';
  resizeHandle.style.transform = 'rotate(-45deg)';
  resizeHandle.addEventListener('mousedown', function (e) {
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

  // ─── Show widget ─────────────────────────────────────────────────────────────

  widget.removeAttribute('hidden');

  // ─── Panel toggle ────────────────────────────────────────────────────────────

  toggle.addEventListener('click', function () {
    if (panel.hasAttribute('hidden')) {
      openPanel();
    } else {
      closePanel();
    }
  });

  closeBtn.addEventListener('click', closePanel);

  function openPanel() {
    panel.removeAttribute('hidden');
    input.focus();
  }

  function closePanel() {
    panel.setAttribute('hidden', '');
  }

  // ─── Markdown renderer ─────────────────────────────────────────────────────

  function renderMarkdown(text) {
    var src = text.replace(/\r\n/g, '\n');

    src = src.replace(/```[\s\S]*?```/g, function (match) {
      var code = match.replace(/^```\w*\n?/, '').replace(/\n?```$/, '');
      return '<pre><code>' + escapeHtml(code) + '</code></pre>';
    });

    var lines = src.split('\n');
    var html = [];
    var i = 0;

    while (i < lines.length) {
      var line = lines[i];

      if (line.indexOf('<pre><code>') === 0) {
        html.push(line);
        i++;
        continue;
      }

      var headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        var level = headingMatch[1].length;
        html.push('<h' + level + '>' + inlineFormat(headingMatch[2]) + '</h' + level + '>');
        i++;
        continue;
      }

      if (/^(---+|\*\*\*+|___+)\s*$/.test(line)) {
        html.push('<hr>');
        i++;
        continue;
      }

      if (/^\s*[\-\*]\s+/.test(line)) {
        var items = [];
        while (i < lines.length && /^\s*[\-\*]\s+/.test(lines[i])) {
          items.push('<li>' + inlineFormat(lines[i].replace(/^\s*[\-\*]\s+/, '')) + '</li>');
          i++;
        }
        html.push('<ul>' + items.join('') + '</ul>');
        continue;
      }

      if (/^\s*\d+\.\s+/.test(line)) {
        var olItems = [];
        while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
          olItems.push('<li>' + inlineFormat(lines[i].replace(/^\s*\d+\.\s+/, '')) + '</li>');
          i++;
        }
        html.push('<ol>' + olItems.join('') + '</ol>');
        continue;
      }

      if (line.trim() === '') {
        i++;
        continue;
      }

      var para = [];
      while (i < lines.length && lines[i].trim() !== '' &&
             !/^#{1,6}\s/.test(lines[i]) &&
             !/^\s*[\-\*]\s+/.test(lines[i]) &&
             !/^\s*\d+\.\s+/.test(lines[i]) &&
             !/^(---+|\*\*\*+|___+)\s*$/.test(lines[i])) {
        para.push(lines[i]);
        i++;
      }
      html.push('<p>' + inlineFormat(para.join(' ')) + '</p>');
    }

    return html.join('');
  }

  function inlineFormat(text) {
    var s = escapeHtml(text);
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/__(.+?)__/g, '<strong>$1</strong>');
    s = s.replace(/\*(.+?)\*/g, '<em>$1</em>');
    s = s.replace(/_(.+?)_/g, '<em>$1</em>');
    return s;
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ─── Message rendering ───────────────────────────────────────────────────────

  function addMsg(text, role) {
    var messageWrapper = document.createElement('div');
    messageWrapper.className = 'display-flex margin-bottom-2';

    var div = document.createElement('div');
    div.className = 'padding-1 radius-md';
    div.style.wordWrap = 'break-word';
    div.style.maxWidth = '66%';

    if (role === 'user') {
      div.className += ' bg-primary text-white';
      div.style.whiteSpace = 'pre-wrap';
      messageWrapper.className += ' flex-justify-end';
    } else if (role === 'assistant') {
      div.className += ' bg-base-lightest text-base-darkest llm-chat-markdown';
      messageWrapper.className += ' flex-justify-start';
    } else if (role === 'error') {
      div.className += ' bg-error-lighter text-error-dark';
      div.style.whiteSpace = 'pre-wrap';
      messageWrapper.className += ' flex-justify-start';
    }

    if (role === 'assistant') {
      div.innerHTML = renderMarkdown(text);
    } else {
      div.textContent = text;
    }

    messages.appendChild(messageWrapper);
    messageWrapper.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function showTyping() {
    var div = document.createElement('div');
    div.className = 'text-base text-italic padding-05';
    div.id = 'llm-chat-typing';
    div.textContent = 'Thinking...';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function removeTyping() {
    var el = document.getElementById('llm-chat-typing');
    if (el) el.remove();
  }

  function setWaiting(waiting) {
    sendBtn.disabled = waiting;
  }

  // ─── API communication ───────────────────────────────────────────────────────

  function postJSON(url, body) {
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(body),
    }).then(function (resp) {
      var contentType = resp.headers.get('Content-Type') || '';
      if (!contentType.includes('application/json')) {
        return { ok: false, data: { error: 'Server returned an unexpected response (status ' + resp.status + ').' } };
      }
      return resp.json().then(function (data) {
        return { ok: resp.ok, data: data };
      });
    });
  }

  function chat(message) {
    openPanel();
    addMsg(message, 'user');
    setWaiting(true);
    showTyping();

    postJSON(chatUrl, { message: message })
      .then(function (result) {
        removeTyping();
        if (result.ok && result.data.response) {
          addMsg(result.data.response, 'assistant');
        } else {
          addMsg(result.data.error || 'Something went wrong.', 'error');
        }
      })
      .catch(function (err) {
        removeTyping();
        addMsg('Network error: ' + err.message, 'error');
      })
      .finally(function () {
        setWaiting(false);
        input.focus();
      });
  }

  function summarize(recordIds) {
    if (!recordIds || recordIds.length === 0) return;

    var label = recordIds.length === 1
      ? 'Summarize this report'
      : 'Summarize & compare ' + recordIds.length + ' reports';

    openPanel();
    addMsg(label, 'user');
    setWaiting(true);
    showTyping();

    postJSON(summarizeUrl, { record_ids: recordIds })
      .then(function (result) {
        removeTyping();
        if (result.ok && result.data.response) {
          addMsg(result.data.response, 'assistant');
        } else {
          addMsg(result.data.error || 'Something went wrong.', 'error');
        }
      })
      .catch(function (err) {
        removeTyping();
        addMsg('Network error: ' + err.message, 'error');
      })
      .finally(function () {
        setWaiting(false);
        input.focus();
      });
  }

  // ─── Input event bindings ────────────────────────────────────────────────────

  sendBtn.addEventListener('click', function () {
    var text = input.value.trim();
    if (!text) return;
    input.value = '';
    chat(text);
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      var text = input.value.trim();
      if (!text) return;
      input.value = '';
      chat(text);
    }
  });

  // ─── Public API ──────────────────────────────────────────────────────────────

  window.LLMChat = {
    addMsg: addMsg,
    openPanel: openPanel,
    closePanel: closePanel,
    showTyping: showTyping,
    removeTyping: removeTyping,
    setWaiting: setWaiting,
    chat: chat,
    summarize: summarize,
  };
})();
