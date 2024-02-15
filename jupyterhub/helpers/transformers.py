import base64
import json
from sql.run.resultset import ResultSet

DISPLAY_NAMES = {
    'cts_forms_report': {
        'status': 'Status',
        'assigned_section': 'Routed',
        'contact_first_name': 'Contact first name',
        'contact_last_name': 'Contact last name',
        'dj_number': 'DJ number',
        'location_city_town': 'Incident city',
        'location_name': 'Organization name',
        'location_state': 'Incident state',
        'assigned_to': 'Assignee',
        'origination_utm_campaign': 'Campaign',
        'public_id': 'Complaint ID',
        'primary_statute': 'Classification',
        'district': 'District number',
        'violation_summary': 'Personal description',
        'primary_complaint': 'Primary issue',
        'servicemember': 'Servicemember',
        'hate_crime': 'Hate crime',
        'intake_format': 'Intake type',
        'commercial_or_public_place': 'Commercial or public place',
        'public_or_private_employer': 'Public or private employer',
        'employer_size': 'Employer size',
        'public_or_private_school': 'Public or private school',
        'inside_correctional_facility': 'Inside correctional facility',
        'correctional_facility_type': 'Prison type',
        'reported_reason': 'Reported reason',
        'summary': 'CRT summary',
        'contact_email': 'Contact email',
        'referred': 'Secondary review',
        'language': 'Report language',
        'create_date': 'Submission date',
        'litigation_hold': 'Litigation hold',
        'retention_schedule': 'Retention schedule',
        'tags': 'Tag',
    }
}

# Add values to this set to enable filtering on a column
FILTERS = {
    'cts_forms_report': {
        'actions',
        'assigned_section',
        'status',
        'contact_first_name',
        'contact_last_name',
        'public_id',
        'assigned_to',
        'origination_utm_campaign',
        'tags',
        'litigation_hold',
        'location_address_line_1',
        'location_address_line_2',
        'location_city_town',
        'location_state',
        'retention_schedule',
        'contact_email',
        'contact_phone',
        'create_date',
        'closed_date',
        'modified_date',
        'primary_statute',
        'district',
        'primary_complaint',
        'dj_number',
        'reported_reason',
        'commercial_or_public_place',
        'servicemember',
        'intake_format',
        'referred',
        'language',
        'hate_crime',
        'correctional_facility_type',
        'violation_summary',
        'summary',
        'location_name',
        'other_class',
        'disposition_status',
    }
}


def column_to_html(table_name, key) -> str:
    display_names = DISPLAY_NAMES.get(table_name, {})
    display = display_names.get(key, key.replace('_', ' ').title())

    filters = FILTERS.get(table_name, {})
    filter_arg = f' data-filter="{key}"' if key in filters else ''

    return f'<th{filter_arg}>{display}</th>'


def result_to_html_table(result: ResultSet, table_name, **kwargs) -> str:
    columns = ''.join([
        column_to_html(table_name, key)
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
