/**
 * LLM Chat – Index Page Integration
 *
 * Monitors table checkbox selections and wires up
 * summarize/compare buttons using the window.LLMChat module.
 *
 * Depends on: llm_chat.js (must be loaded first)
 */
(function () {
  'use strict';

  if (!window.LLMChat) return;

  var widget = document.getElementById('llm-chat-widget');
  if (!widget) return;

  // Only activate on pages with the complaints table checkboxes
  var tables = document.querySelectorAll('.usa-table.crt-table');
  if (!tables.length) return;

  var quickActions = document.getElementById('llm-chat-quick-actions');
  var summarizeBtn = document.getElementById('llm-chat-summarize');
  var summarizeMultipleBtn = document.getElementById('llm-chat-summarize-multiple');
  var summarizeBtnText = widget.querySelector('.llm-chat-summarize-text');
  var summarizeMultipleBtnText = widget.querySelector('.llm-chat-summarize-multiple-text');

  if (!quickActions || !summarizeBtn) return;

  var currentReportIds = [];
  var actionNotification = document.querySelector('.selection-action-notification');

  // ─── Position adjustment ─────────────────────────────────────────────────────

  function adjustWidgetPosition() {
    if (actionNotification && !actionNotification.hidden) {
      var notifHeight = actionNotification.offsetHeight;
      widget.style.bottom = (notifHeight + 12) + 'px';
    } else {
      widget.style.bottom = '';
    }
  }

  // ─── Checkbox state ──────────────────────────────────────────────────────────

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
      widget.dataset.reportId = ids[0];
      quickActions.removeAttribute('hidden');
      if (summarizeBtnText) summarizeBtnText.textContent = 'Summarize report #' + ids[0];
      summarizeBtn.removeAttribute('hidden');
      if (summarizeMultipleBtn) summarizeMultipleBtn.setAttribute('hidden', '');
    } else if (ids.length > 1) {
      widget.dataset.reportId = '';
      quickActions.removeAttribute('hidden');
      summarizeBtn.setAttribute('hidden', '');
      if (summarizeMultipleBtn) {
        summarizeMultipleBtn.removeAttribute('hidden');
        if (summarizeMultipleBtnText) {
          summarizeMultipleBtnText.textContent = 'Summarize & compare ' + ids.length + ' reports';
        }
      }
    } else {
      currentReportIds = [];
      widget.dataset.reportId = '';
      quickActions.setAttribute('hidden', '');
      if (summarizeBtnText) summarizeBtnText.textContent = 'Summarize this report';
      summarizeBtn.removeAttribute('hidden');
      if (summarizeMultipleBtn) summarizeMultipleBtn.setAttribute('hidden', '');
    }
    adjustWidgetPosition();
  }

  // ─── Table event listeners ───────────────────────────────────────────────────

  for (var t = 0; t < tables.length; t++) {
    tables[t].addEventListener('change', function (e) {
      if (e.target && e.target.matches('input.usa-checkbox__input')) {
        updateSummarizeVisibility();
      }
    });

    tables[t].addEventListener('click', function (e) {
      if (e.target && e.target.matches('input.usa-checkbox__input')) {
        setTimeout(updateSummarizeVisibility, 0);
      }
    });
  }

  // ─── Summarize buttons ───────────────────────────────────────────────────────

  summarizeBtn.addEventListener('click', function () {
    if (currentReportIds.length !== 1) return;
    window.LLMChat.summarize(currentReportIds);
  });

  if (summarizeMultipleBtn) {
    summarizeMultipleBtn.addEventListener('click', function () {
      if (currentReportIds.length < 2) return;
      window.LLMChat.summarize(currentReportIds);
    });
  }

  // Run initial check in case page loads with pre-selected checkboxes
  updateSummarizeVisibility();
})();
