(function(root, dom) {
  function copyContents(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
  }

  function addCopyButtonListener(copyButton, parentTable, actionNotificationEl, countEl) {
    const checkBoxes = parentTable.querySelectorAll('td input.usa-checkbox__input:checked');
    copyButton.addEventListener('click', e => {
      e.preventDefault();
      const resources = [];
      checkBoxes.forEach(checkBox => {
        const row = checkBox.closest('.tr--hover');
        const resourceText = row.querySelector('.copy-text');
        resources.push(resourceText.textContent);
      });
      copyContents(resources.join(''));
      copyButton.hidden = true;
      countEl.innerText = 'Saved to clipboard!';
      setTimeout(() => {
        actionNotificationEl.hidden = true;
      }, 2000);
    });
  }

  function updateResourceCount(index, parentTable) {
    const actionNotificationEls = dom.getElementsByClassName('selection-action-notification');
    const actionNotificationEl = actionNotificationEls[index];
    const countEl = actionNotificationEl.getElementsByClassName('selection-action-count')[0];
    const copyButton = actionNotificationEl.getElementsByTagName('button')[0];
    const count = parentTable.querySelectorAll('td input.usa-checkbox__input:checked').length;
    if (count === 0) {
      actionNotificationEl.hidden = true;
    } else {
      const resourcesPlural = count === 1 ? ' resource ' : ' resources ';
      countEl.innerText = count + resourcesPlural + 'selected';
      copyButton.hidden = false;
      copyButton.innerText = 'Copy' + resourcesPlural;
      actionNotificationEl.hidden = false;
    }
    addCopyButtonListener(copyButton, parentTable, actionNotificationEl, countEl);
  }

  function addCheckAllListener(selectAllCheckbox, allCheckboxes) {
    selectAllCheckbox.addEventListener('click', event => {
      const checked = event.target.checked;
      allCheckboxes.forEach(checkbox => {
        if (checkbox.checked !== checked) {
          checkbox.click();
        }
      });
    });
  }

  function addCheckboxListener(checkbox, index, parentTable) {
    checkbox.addEventListener('click', event => {
      const target = event.target;
      const parent = target.parentNode.parentNode.parentNode;
      if (target.checked) {
        parent.classList.add('selected');
      } else {
        parent.classList.remove('selected');
        if (selectAllCheckboxes[index].checked) {
          selectAllCheckboxes[index].checked = false;
        }
      }
      updateResourceCount(index, parentTable);
    });
  }

  function isToggled(target) {
    return target.getAttribute('aria-expanded') === 'true';
  }

  function toggleTarget(toggle) {
    const arrow = toggle.querySelector('.icon');
    const id = toggle.dataset['id'];
    const summary = dom.getElementById(`tr-additional-${id}`);
    toggle.setAttribute('aria-expanded', isToggled(toggle) ? 'false' : 'true');
    arrow.classList.toggle('rotate');
    summary.toggleAttribute('hidden');
  }

  function addToggleListener(toggleAll, parentTable) {
    toggleAll.addEventListener('click', event => {
      event.preventDefault();
      const allToggled = isToggled(toggleAll);
      toggleAll.querySelector('.icon').classList.toggle('rotate');
      toggleAll.setAttribute('aria-expanded', allToggled ? 'false' : 'true');
      const toggles = [...parentTable.querySelectorAll('a.td-toggle')].filter(
        toggle => isToggled(toggle) == allToggled
      );

      toggles.forEach(toggle => toggleTarget(toggle));
    });
  }

  function copyRow(e) {
    const row = e.target.closest('.tr--hover');
    const resourceText = row.querySelector('.copy-text').textContent;
    copyContents(resourceText);
    const copyText = row.getElementsByClassName('copied')[0];
    const copyIcon = row.getElementsByClassName('copy-resource')[0];
    copyText.style.display = 'block';
    copyIcon.style.display = 'none';
    setTimeout(() => {
      copyText.style.display = 'none';
      copyIcon.style.display = 'block';
    }, 2000);
  }

  function setUpEventListeners() {
    const selectAllCheckboxes = dom.getElementsByClassName('checkbox-input-all');
    for (let index = 0; index < selectAllCheckboxes.length; index++) {
      const parentTable = selectAllCheckboxes[index].closest('.usa-table.crt-table');
      const allCheckboxes = parentTable.querySelectorAll('td input.usa-checkbox__input');
      allCheckboxes.forEach(checkbox => {
        addCheckboxListener(checkbox, index, parentTable);
      });
      addCheckAllListener(selectAllCheckboxes[index], allCheckboxes);
    }

    const copyButtons = document.querySelectorAll('.copy-resource');
    copyButtons.forEach(function(btn) {
      btn.onclick = function(event) {
        event.preventDefault();
        copyRow(event);
      };
    });

    const searchInput = document.querySelector('#id_search');
    searchInput.oninput = function(event) {
      event.preventDefault();
      setTimeout(() => {
        makeQuery();
      }, 1500);
    };

    const tagInput = document.querySelector('#id_tags-assign-tag');
    tagInput.onchange = function() {
      makeQuery();
    };

    const tagOptions = document.querySelectorAll('.usa-selected-tags > .tag-option');
    tagOptions.forEach(function(tagOption) {
      tagOption.onclick = function(event) {
        makeQuery(event, 'remove_tag');
      };
    });

    const sortLinks = document.querySelectorAll('.sort-link');
    sortLinks.forEach(function(btn) {
      btn.onclick = function(event) {
        event.preventDefault();
        makeQuery(event, 'sort');
      };
    });

    const toggles = dom.querySelectorAll('a.td-toggle');
    toggles.forEach(function(toggle) {
      toggle.onclick = function(event) {
        const target = event.currentTarget;
        const id = target.dataset['id'];
        const image = target.children[0];
        const row = dom.getElementById('tr-additional-' + id);
        if (target.getAttribute('aria-expanded') === 'true') {
          target.setAttribute('aria-expanded', 'false');
          image.classList.remove('rotate');
          row.setAttribute('hidden', '');
        } else {
          target.setAttribute('aria-expanded', 'true');
          image.classList.add('rotate');
          row.removeAttribute('hidden');
        }
        event.preventDefault();
      };
    });

    const toggleAllButtons = dom.querySelectorAll('.td-toggle-all');
    toggleAllButtons.forEach(toggleAll => {
      const parentTable = toggleAll.closest('.usa-table.crt-table');
      addToggleListener(toggleAll, parentTable);
    });

    const per_pages = Array.from(document.getElementsByName('per_page'));
    per_pages.forEach(function(per_page) {
      per_page.onchange = function(event) {
        event.preventDefault();
        makeQuery();
      };
    });

    const pages = document.querySelectorAll('.pagination > li > a');
    pages.forEach(function(page) {
      page.onclick = function(event) {
        event.preventDefault();
        makeQuery(event, 'page');
      };
    });
  }

  function updateContent(data) {
    const resources = data.html;
    const wrapper = document.createElement('div');
    wrapper.className = 'resource-table';
    wrapper.innerHTML = resources;
    resourcesWrapper.appendChild(wrapper);
    const resourcesTable = resourcesWrapper.querySelectorAll('.resource-table');
    if (resourcesTable.length > 1) {
      resourcesTable[0].remove();
    }
    setUpEventListeners();
  }

  function getTagParams(apiUrl, type, event) {
    const tags = Array.from(dom.querySelectorAll('.tag-option > input:checked'))
      .map(tag => tag.value)
      .filter(tag => tag != null);
    if (type == 'remove_tag') {
      const value = event.target.closest('div').querySelector('input').value;
      const index = tags.indexOf(value);
      if (index > -1) {
        tags.splice(index, 1);
      }
    }
    if (tags.length) {
      tags.forEach(tag => (apiUrl += `&tag=${tag}`));
    }
    return apiUrl;
  }

  function makeQuery(event = null, type = null) {
    let apiUrl = '/api/resources-list/?';
    apiUrl += type == 'sort' ? event.target.getAttribute('href').substring(1) : '';
    apiUrl += type == 'page' ? event.target.getAttribute('href') : '';

    const per_pages = Array.from(document.getElementsByName('per_page'));
    apiUrl += per_pages.length === 1 ? `&per_page=${per_pages[0].value}` : '';

    apiUrl = getTagParams(apiUrl, type, event);

    const search_term = dom.querySelector('#id_search').value;
    apiUrl += search_term ? `&search_term=${search_term}` : '';

    window
      .fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        mode: 'same-origin'
      })
      .then(response => response.json().then(data => updateContent(data)))
      .catch(error => {
        console.log(error);
      });
  }

  const resourcesWrapper = document.querySelector('.resources-wrapper');
  makeQuery();
})(window, document);
