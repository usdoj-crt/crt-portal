// Progressive enhancement for the News widget column admin.
//
// Converts the article JSON <textarea> into a friendly add / remove / reorder
// editor with a native date picker per article. The <textarea> stays the source
// of truth that is submitted, so the "Show raw JSON" toggle lets power users
// edit the JSON directly. Dates are stored as ISO (YYYY-MM-DD); the public page
// formats them for display.
(function () {
  'use strict';

  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function pad2(value) {
    return String(value).padStart(2, '0');
  }

  // Normalize a stored date into an ISO 'YYYY-MM-DD' string for <input type=date>.
  // Accepts ISO input as-is, or the legacy display format e.g. 'Feb 26, 2026'.
  function toIso(value) {
    if (!value) {
      return '';
    }
    value = String(value).trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      return value;
    }
    var match = /^([A-Za-z]{3,})\.?\s+(\d{1,2}),\s*(\d{4})$/.exec(value);
    if (!match) {
      return '';
    }
    var abbreviation = match[1].slice(0, 3).toLowerCase();
    var monthIndex = -1;
    for (var i = 0; i < MONTHS.length; i++) {
      if (MONTHS[i].toLowerCase() === abbreviation) {
        monthIndex = i;
        break;
      }
    }
    if (monthIndex < 0) {
      return '';
    }
    return match[3] + '-' + pad2(monthIndex + 1) + '-' + pad2(parseInt(match[2], 10));
  }

  // Parse the textarea JSON into a normalized array of article objects.
  // Throws if the JSON is invalid or is not an array.
  function parseArticles(raw) {
    if (!raw || !raw.trim()) {
      return [];
    }
    var parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      throw new Error('Expected a JSON array of articles.');
    }
    return parsed.map(function (item) {
      item = item || {};
      return {
        date: toIso(item.date) || '',
        title: item.title || '',
        link: item.link || ''
      };
    });
  }

  function makeButton(label, className) {
    var button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    button.className = className;
    return button;
  }

  function initEditor(editor) {
    var textarea = editor.querySelector('[data-news-article-json]');
    var rowsContainer = editor.querySelector('[data-news-article-rows]');
    var addButton = editor.querySelector('[data-news-article-add]');
    var toggleButton = editor.querySelector('[data-news-article-toggle-raw]');
    if (!textarea || !rowsContainer || !addButton || !toggleButton) {
      return;
    }

    var articles;
    try {
      articles = parseArticles(textarea.value);
    } catch (error) {
      // Invalid JSON: leave the raw textarea visible so it can be fixed.
      showRawFallback(editor, textarea, rowsContainer, addButton, toggleButton);
      return;
    }

    function sync() {
      textarea.value = JSON.stringify(articles, null, 2);
    }

    function render() {
      rowsContainer.textContent = '';
      articles.forEach(function (article, index) {
        rowsContainer.appendChild(buildRow(article, index));
      });
    }

    function bindInput(input, index, field) {
      input.addEventListener('input', function () {
        articles[index][field] = input.value;
        sync();
      });
    }

    function buildRow(article, index) {
      var row = document.createElement('div');
      row.className = 'news-article-editor__row';

      var dateInput = document.createElement('input');
      dateInput.type = 'date';
      dateInput.className = 'news-article-editor__date';
      dateInput.value = article.date;
      dateInput.setAttribute('aria-label', 'Article date');
      bindInput(dateInput, index, 'date');

      var titleInput = document.createElement('input');
      titleInput.type = 'text';
      titleInput.className = 'news-article-editor__title';
      titleInput.placeholder = 'Article title';
      titleInput.value = article.title;
      titleInput.setAttribute('aria-label', 'Article title');
      bindInput(titleInput, index, 'title');

      var linkInput = document.createElement('input');
      linkInput.type = 'url';
      linkInput.className = 'news-article-editor__link';
      linkInput.placeholder = 'https://...';
      linkInput.value = article.link;
      linkInput.setAttribute('aria-label', 'Article link');
      bindInput(linkInput, index, 'link');

      var buttons = document.createElement('div');
      buttons.className = 'news-article-editor__row-buttons';

      var upButton = makeButton('\u2191', 'button news-article-editor__move');
      upButton.title = 'Move up';
      upButton.disabled = index === 0;
      upButton.addEventListener('click', function () {
        move(index, index - 1);
      });

      var downButton = makeButton('\u2193', 'button news-article-editor__move');
      downButton.title = 'Move down';
      downButton.disabled = index === articles.length - 1;
      downButton.addEventListener('click', function () {
        move(index, index + 1);
      });

      var removeButton = makeButton('Remove', 'button news-article-editor__remove');
      removeButton.addEventListener('click', function () {
        articles.splice(index, 1);
        sync();
        render();
      });

      buttons.appendChild(upButton);
      buttons.appendChild(downButton);
      buttons.appendChild(removeButton);

      row.appendChild(dateInput);
      row.appendChild(titleInput);
      row.appendChild(linkInput);
      row.appendChild(buttons);
      return row;
    }

    function move(from, to) {
      if (to < 0 || to >= articles.length) {
        return;
      }
      var moved = articles.splice(from, 1)[0];
      articles.splice(to, 0, moved);
      sync();
      render();
    }

    addButton.addEventListener('click', function () {
      articles.push({ date: '', title: '', link: '' });
      sync();
      render();
    });

    var rawVisible = false;
    toggleButton.addEventListener('click', function () {
      if (!rawVisible) {
        // Show raw: textarea already mirrors the current editor state.
        rawVisible = true;
        textarea.hidden = false;
        rowsContainer.hidden = true;
        addButton.hidden = true;
        toggleButton.textContent = 'Hide raw JSON';
        return;
      }
      // Hide raw: re-parse any manual edits back into the friendly editor.
      try {
        articles = parseArticles(textarea.value);
      } catch (error) {
        window.alert('The raw JSON is invalid, so it cannot be shown in the editor. Please fix the JSON first.');
        return;
      }
      rawVisible = false;
      sync();
      render();
      textarea.hidden = true;
      rowsContainer.hidden = false;
      addButton.hidden = false;
      toggleButton.textContent = 'Show raw JSON';
    });

    // Initial state: friendly editor visible, raw textarea hidden by JS
    // (it starts visible in the HTML so it still works without JavaScript).
    sync();
    render();
    textarea.hidden = true;
  }

  function showRawFallback(editor, textarea, rowsContainer, addButton, toggleButton) {
    rowsContainer.hidden = true;
    addButton.hidden = true;
    toggleButton.hidden = true;
    var note = document.createElement('p');
    note.className = 'news-article-editor__error';
    note.textContent = 'The stored JSON could not be parsed, so it is shown raw below for you to fix.';
    editor.insertBefore(note, textarea);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var editors = document.querySelectorAll('[data-news-article-editor]');
    for (var i = 0; i < editors.length; i++) {
      initEditor(editors[i]);
    }
  });
})();
