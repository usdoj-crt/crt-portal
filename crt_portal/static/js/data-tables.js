(function(root, dom) {
  function getData(table, fieldName) {
    b64 = table.dataset[fieldName];
    if (!b64) return undefined;
    return JSON.parse(atob(b64));
  }

  function getOptions(table) {
    const options = {
      colReorder: true,
      select: true,
      buttons: [
        {
          extend: 'searchPanes',
          config: {
            cascadePanes: true
          }
        },
        'spacer',
        'copyHtml5',
        'excelHtml5',
        'print',
        'spacer',
        'colvis',
        'spacer',
        'selectAll',
        'selectNone'
      ],
      dom: 'Bfrtip'
    };

    columns = getData(table, 'columns');
    if (columns) options.columns = columns;

    rows = getData(table, 'rows');
    if (rows) options.data = rows;

    return options;
  }

  function buildFilterDropdown(label) {
    dropdown = $(`
      <div class="crt-dropdown" data-crt-dropdown="">
        <button class="crt-dropdown__title" aria-controls="date" aria-expanded="false" type="button" id="date" data-crt-dropdown-control="">
          <span class="label">${label}</span>
          <img src="/static/img/intake-icons/ic_select-down.svg" alt="open filter dropdown" class="icon">
        </button>
        <div class="content" hidden>
        </div>
      </div>
    `);
    root.addCRTDropdown(dropdown[0]);
    return dropdown;
  }

  function buildDateFilter(dateIndex) {
    return $(`
      <div class="date-picker column-${dateIndex}">
        <label class="usa-label">
          From:
          <input type="date" class="usa-input min" min="2019-01-01" placeholder="yyyy-mm-dd">
        </label>
        <label class="usa-label">
          To:
          <input type="date" class="usa-input max" min="2019-01-01" placeholder="yyyy-mm-dd">
        </label>
      </div>
    `);
  }

  function addDateFilter(dataTable, column, dateIndex) {
    const dateFilter = buildDateFilter(dateIndex);
    const wrapper = $('.dataTables_wrapper');
    const filterDropdown = buildFilterDropdown(column);

    filterDropdown.find('.content').append(dateFilter);
    wrapper.prepend(filterDropdown);

    const minDate = dateFilter.find('input.min');
    const maxDate = dateFilter.find('input.max');

    DataTable.ext.search.push(function(settings, data, dataIndex) {
      const rawMin = minDate.val();
      const rawMax = maxDate.val();
      const min = rawMin ? new Date(rawMin) : null;
      const max = rawMax ? new Date(rawMax) : null;

      const date = new Date(data[dateIndex]);

      if (min === null && max === null) return true;
      if (min === null && date <= max) return true;
      if (min <= date && max === null) return true;
      if (min <= date && date <= max) return true;
      return false;
    });

    minDate.on('change', () => dataTable.draw());
    maxDate.on('change', () => dataTable.draw());
  }

  function setupFilters(table, dataTable) {
    $(table)
      .find('thead th')
      .each((index, th) => {
        const column = $(th).text();

        if (column.includes('Date')) {
          addDateFilter(dataTable, column, index);
        }
      });
  }

  $(document).ready(function() {
    $('.datatable-table').each((index, table) => {
      options = getOptions(table);

      const dataTable = $(table).DataTable(options);

      setupFilters(table, dataTable);
    });
  });
})(window, document);
