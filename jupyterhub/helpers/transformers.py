import base64
import json
from sql.run.resultset import ResultSet


def result_to_html_table(result: ResultSet, **kwargs) -> str:
    columns = ''.join([
        f'<th>{key}</th>'
        for key in result.keys
    ])

    rows = json.dumps([
        *result.DataFrame().astype(str).to_numpy().tolist(),
    ], separators=(',', ':'))
    rows_encoded = base64.b64encode(rows.encode('utf-8')).decode('utf-8')

    extra_data = '\n'.join([
        f'data-{key}={value}'
        for key, value in kwargs.items()
    ])

    return f'''
        <table
            data-rows="{rows_encoded}"
            {extra_data}
            class="datatable-table">
            <thead>{columns}</thead>
        </table>
    '''
