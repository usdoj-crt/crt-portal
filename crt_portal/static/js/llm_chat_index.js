(function() {
  'use strict';

  var widget = document.getElementById('llm-chat-widget');
  if (!widget) return;

  // Only activate on pages with the complaints table checkboxes
  var tables = document.querySelectorAll('.usa-table.crt-table');
  if (!tables.length) return;

  var quickActions = document.getElementById('llm-chat-quick-actions');
  var summarizeBtn = document.getElementById('llm-chat-summarize');
  var summarizeMultipleBtn = document.getElementById('llm-chat-summarize-multiple');
  var summarzieBtnText = document.getElementById('llm-chat-summarize-text')
  var summarzieMultipleBtnText = document.getElementById('llm-chat-summarize-multiple-text')
  var messages = document.getElementById('llm-chat-messages');
  var sendBtn = document.getElementById('llm-chat-send');
  var input = document.getElementById('llm-chat-input');

  if (!quickActions || !summarizeBtn) return;

  var currentReportId = null;
  var currentReportIds = [];
  var actionNotification = document.querySelector('.selection-action-notification');

  function adjustWidgetPosition() {
    if (actionNotification && !actionNotification.hidden) {
      var notifHeight = actionNotification.offsetHeight;
      widget.style.bottom = (notifHeight + 12) + 'px';
    } else {
      widget.style.bottom = '';
    }
  }

  function getCheckedIds() {
    var ids = [];
    for (var t = 0; t < tables.length; t++) {
      var checkboxes = tables[t].querySelectorAll('td input.usa-checkbox__input:checked');
      for (var i = 0; i < checkboxes.length; i++) {
        ids.push(checkboxes[i].value);
      }
    }
    return ids;
  }

  function updateSummarizeVisibility() {
    var ids = getCheckedIds();
    currentReportIds = ids;

    if (ids.length === 1) {
      currentReportId = ids[0];
      widget.dataset.reportId = currentReportId;
      quickActions.removeAttribute('hidden');
      summarizeBtnText.textContent = 'Summarize report #' + currentReportId;
      summarizeBtn.removeAttribute('hidden');
      if (summarizeMultipleBtn) summarizeMultipleBtn.setAttribute('hidden', '');
    } else if (ids.length > 1) {
      currentReportId = null;
      widget.dataset.reportId = '';
      quickActions.removeAttribute('hidden');
      summarizeBtn.setAttribute('hidden', '');
      if (summarizeMultipleBtn) {
        summarizeMultipleBtn.removeAttribute('hidden');
        summarizeMultipleBtnText.textContent = 'Summarize & compare ' + ids.length + ' reports';
      }
    } else {
      currentReportId = null;
      currentReportIds = [];
      widget.dataset.reportId = '';
      quickActions.setAttribute('hidden', '');
      summarizeBtnText.textContent = 'Summarize this report';
      summarizeBtn.removeAttribute('hidden');
      if (summarizeMultipleBtn) summarizeMultipleBtn.setAttribute('hidden', '');
    }
    adjustWidgetPosition();
  }

  // Listen for checkbox changes in all tables
  for (var t = 0; t < tables.length; t++) {
    tables[t].addEventListener('change', function(e) {
      if (e.target && e.target.matches('input.usa-checkbox__input')) {
        updateSummarizeVisibility();
      }
    });

    // Also listen for clicks (the "select all" checkbox triggers click events)
    tables[t].addEventListener('click', function(e) {
      if (e.target && e.target.matches('input.usa-checkbox__input')) {
        // Use setTimeout to let the checkbox state settle
        setTimeout(updateSummarizeVisibility, 0);
      }
    });
  }

  // Helper functions (duplicated from llm_chat.js since they're in a closure)
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

    if (role === 'assistant' && window.marked) {
      div.innerHTML = window.marked.parse(text);
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

  function getCookie(name) {
    var match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  function disableButtons() {
    summarizeBtn.disabled = true;
    if (summarizeMultipleBtn) summarizeMultipleBtn.disabled = true;
    sendBtn.disabled = true;
  }

  function enableButtons() {
    summarizeBtn.disabled = false;
    if (summarizeMultipleBtn) summarizeMultipleBtn.disabled = false;
    sendBtn.disabled = false;
  }

  // Replace the summarize button to remove old event listeners from llm_chat.js
  var newSummarizeBtn = summarizeBtn.cloneNode(true);
  summarizeBtn.parentNode.replaceChild(newSummarizeBtn, summarizeBtn);
  summarizeBtn = newSummarizeBtn;

  // Single report summarize
  summarizeBtn.addEventListener('click', function() {
    if (!currentReportId) return;
    disableButtons();
    addMsg('Summarize report #' + currentReportId, 'user');
    showTyping();

    fetch('/form/view/' + currentReportId + '/llm/summarize/', {
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
      enableButtons();
      if (input) input.focus();
    });
  });

  // Multiple reports summarize & compare
  if (summarizeMultipleBtn) {
    summarizeMultipleBtn.addEventListener('click', function() {
      if (currentReportIds.length < 2) return;
      disableButtons();
      addMsg('Summarize & compare ' + currentReportIds.length + ' reports', 'user');
      showTyping();

      fetch('/form/llm/summarize-reports/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ ids: currentReportIds })
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
        enableButtons();
        if (input) input.focus();
      });
    });
  }

  // Run initial check in case page loads with pre-selected checkboxes
  updateSummarizeVisibility();
})();
