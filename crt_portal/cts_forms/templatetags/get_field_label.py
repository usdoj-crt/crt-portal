from django import template
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
register = template.Library()

# TODO: where possible, pull in names from filter labels
variable_rename = {
    'status': 'Status',
    'assigned_section': 'Routed',
    'contact_first_name': 'Contact first name',
    'contact_last_name': 'Contact last name',
    'location_city_town': 'Incident city',
    'location_name': 'Incident location name',
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
    'commercial_or_public_place': 'Relevant details',
    'reported_reason': 'Reported reason',
    'summary': 'CRT summary',
    'contact_email': 'Contact email',
    'referred': 'Secondary review',
    'language': 'Report language',
    'correctional_facility_type': 'Prison type',
    'create_date_start': 'Submission date start',
    'create_date_end': 'Submission date end',
    'actions': 'Actions',
    'litigation_hold': 'Litigation hold',
    'retention_schedule': 'Retention schedule',
}


@register.filter(name='get_field_label')
def get_field_label(value, arg):
    """
    Return label for given model/field from cts_forms app
    If no field exists, we expect it's a filter field like
    `create_date_end',  strip underscores for display
    """
    try:
        model = apps.get_model('cts_forms', value)
        field = model._meta.get_field(arg)
    except FieldDoesNotExist:
        return variable_rename.get(arg, arg.replace('_', ' '))

    return variable_rename.get(field.name, field.verbose_name)
