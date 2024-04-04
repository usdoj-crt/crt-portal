(function(root, dom) {
  function getData(table, fieldName) {
    b64 = table.dataset[fieldName];
    if (!b64) return undefined;
    return JSON.parse(atob(b64));
  }

  function getFilters(tableOrApi) {
    const filters = [];
    if (tableOrApi instanceof DataTable.Api) {
      tableOrApi.columns().every(function() {
        if (!this.visible()) {
          filters.push(null);
          return;
        }
        const filter = this.header().dataset.filter;
        filters.push(filter);
      });
      return filters;
    }

    const headers = [...tableOrApi.querySelectorAll('thead th')];
    return headers.map(th => th.dataset.filter);
  }

  const SECTIONS =
    '&assigned_section=ADM&assigned_section=APP&assigned_section=CRM&assigned_section=DRS&assigned_section=ELS&assigned_section=EOS&assigned_section=FCS&assigned_section=HCE&assigned_section=IER&assigned_section=POL&assigned_section=SPL&assigned_section=VOT';

  function buildRowLink(filters, row) {
    const filterMap = filters.reduce((soFar, filter, columnIndex) => {
      if (!filter) return soFar;
      soFar[filter] = row[columnIndex];
      return soFar;
    }, {});

    const queryString = new URLSearchParams(filterMap).toString();
    const sections = filterMap['assigned_section'] ? '' : SECTIONS;
    return `/form/view/?${queryString}${sections}`;
  }

  function maybeAddViewAllHeader(tableOrApi) {
    const table = $(tableOrApi instanceof DataTable.Api ? tableOrApi.table().node() : tableOrApi);
    if (table.find('thead th.view-all').length) return;
    table.find('thead tr').append('<th class="view-all">View all</th>');
  }

  function addViewAll(tableOrApi, rows) {
    const filters = getFilters(tableOrApi);
    if (filters.every(filter => !filter)) {
      rows.forEach(row => {
        row.push('N/A');
      });
      return;
    }

    maybeAddViewAllHeader(tableOrApi, filters);

    rows.forEach(row => {
      const link = buildRowLink(filters, row);
      row.push(`<a class="view-all" href="${link}">View all</a>`);
    });
  }

  function getOptions(table) {
    const options = {
      colReorder: true,
      select: true,
      language: {
        searchPanes: {
          clearMessage: 'Clear all filters'
        }
      },
      buttons: [
        {
          extend: 'searchPanes',
          text: 'Filter',
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

    const rows = getData(table, 'rows');
    if (rows) {
      saveRows(rows);
      addViewAll(table, rows);
      options.data = rows;
    }

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

  function saveRows(rows) {
    sessionStorage.setItem('dataDashboardContent', JSON.stringify(rows));
  }

  function readRows() {
    return JSON.parse(sessionStorage.getItem('dataDashboardContent'));
  }

  /**
   * Reduces duplication in table rows while aggregating data.
   *
   * If a row's name includes "(sum)",
   * it will be added to other rows that are otherwise the same
   */
  function aggregate(rows, dataTable) {
    const aggregates = {};

    const allColumnIndices = dataTable.columns().indexes();
    const allColumns = dataTable
      .columns()
      .header()
      .map(h => h.innerText);
    const isColumnVisible = dataTable.columns().visible();
    const visibleIndices = Array.from(allColumnIndices).filter(i => isColumnVisible[i]);
    const visibleColumns = dataTable
      .columns(visibleIndices)
      .header()
      .map(h => h.innerText);
    const groupBy = Array.from(visibleColumns.filter(c => !c.toLowerCase().includes('(sum)')));
    const groupByIndices = groupBy.map(col => allColumns.indexOf(col));
    const sum = Array.from(visibleColumns.filter(c => c.toLowerCase().includes('(sum)')));
    const sumIndices = sum.map(col => allColumns.indexOf(col));

    rows.forEach(row => {
      const key = groupByIndices.reduce((soFar, col) => `${soFar}|${row[col]}`, '');
      if (!aggregates.hasOwnProperty(key)) {
        aggregates[key] = groupByIndices.reduce((soFar, col) => {
          soFar[col] = row[col];
          return soFar;
        }, {});
      }
      sumIndices.forEach(col => {
        aggregates[key][col] = (aggregates[key][col] || 0) + Number(row[col]);
      });
    });

    if (allColumns[allColumns.length - 1].toLowerCase() === 'view all') {
      allColumnIndices.pop();
    }

    const groupedRows = Object.values(aggregates).map(row => {
      return allColumnIndices.map(col => (row.hasOwnProperty(col) ? row[col] : ''));
    });

    addViewAll(dataTable, groupedRows);

    dataTable.clear();
    dataTable.rows.add(groupedRows);
    return dataTable;
  }

  $(document).ready(function() {
    $('.datatable-table').each((index, table) => {
      options = getOptions(table);

      const dataTable = $(table).DataTable(options);
      setupFilters(table, dataTable);
      dataTable.draw();

      $(table).on('column-visibility.dt', function() {
        aggregate(readRows(), dataTable).draw();
      });
    });
  });
})(window, document);
