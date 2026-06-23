/**
 * LLM Chat – Detail View Integration
 *
 * Wires up the summarize button for a single report on the detail page.
 * Reads the report ID from the widget's data-report-id attribute.
 *
 * Depends on: llm_chat.js (must be loaded first)
 */
(function () {
  'use strict';

  if (!window.LLMChat) return;

  var widget = document.getElementById('llm-chat-widget');
  if (!widget) return;

  var reportId = widget.dataset.reportId;
  if (!reportId) return;

  var quickActions = document.getElementById('llm-chat-quick-actions');
  var summarizeBtn = document.getElementById('llm-chat-summarize');
  var summarizeMultipleBtn = document.getElementById('llm-chat-summarize-multiple');
  var summarizeBtnText = widget.querySelector('.llm-chat-summarize-text');

  if (!quickActions || !summarizeBtn) return;

  // Show summarize quick action for this single report
  quickActions.removeAttribute('hidden');
  if (summarizeBtnText) {
    summarizeBtnText.textContent = 'Summarize report #' + reportId;
  }
  summarizeBtn.removeAttribute('hidden');
  if (summarizeMultipleBtn) summarizeMultipleBtn.setAttribute('hidden', '');

  // Wire up the summarize button
  summarizeBtn.addEventListener('click', function () {
    window.LLMChat.summarize([reportId]);
  });
})();
