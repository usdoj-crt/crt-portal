import logging
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
    'create_date_start': 'Submission date start',
    'create_date_end': 'Submission date end',
    'actions': 'Actions',
    'litigation_hold': 'Litigation hold',
    'retention_schedule': 'Retention schedule',
    'tags': 'Tag',
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


def _get_tag_attrs(tag_id, *attrs):
    Tag = apps.get_model('cts_forms', 'Tag')
    tags = Tag.objects.filter(id=tag_id).values(*attrs)
    if not tags:
        return [''] * len(attrs)
    return tuple([tags[0][attr] for attr in attrs])


def _get_tags_markup(field_content):
    section, name, tooltip = _get_tag_attrs(field_content, 'section', 'name', 'tooltip')
    return f'''
    <span class="usa-tooltip" data-position="right" data-classes="display-inline" title="{tooltip}">
        <span class="usa-tag usa-tag--big">
            <span class="section">{section}</span>
            <span class="name">{name}</span>
        </span>
    </span>
    '''


def _prepare_fuzzy_for_chip(key, filters):
    prefix = filters.get(key, [''])[0]

    if not prefix:
        return

    sounds_like_value = filters.pop(f'{key}_1', [''])[0]
    suffix = []
    if sounds_like_value and sounds_like_value != '0':
        level = ''
        if sounds_like_value == 2:
            level = 'low'
        if sounds_like_value == 5:
            level = 'medium'
        if sounds_like_value == 8:
            level = 'high'
        suffix.append(f'{level} sounds like inclusivity')

    looks_like_value = filters.pop(f'{key}_2', [''])[0]
    if looks_like_value and looks_like_value != '0':
        level = ''
        if looks_like_value == 2:
            level = 'low'
        if looks_like_value == 5:
            level = 'medium'
        if looks_like_value == 8:
            level = 'high'
        suffix.append(f'{level} looks like inclusivity')

    if not suffix:
        suffix.append('exact match')
    suffix = ' and '.join(suffix)
    filters[key] = [f'{prefix} ({suffix})']


@register.filter(name='prepare_filters_for_chips')
def prepare_filters_for_chips(filters):
    if not filters:
        return {}
    filters = dict(filters)
    for fuzzy_filter in ['location_name']:
        _prepare_fuzzy_for_chip(fuzzy_filter, filters)
    return filters


@register.filter(name='get_field_markup')
def get_field_markup(field_content, field_name) -> str:
    if field_name == 'tags':
        return _get_tags_markup(field_content)
    return field_content


def _get_tags_plaintext(field_content):
    section, name = _get_tag_attrs(field_content, 'section', 'name')
    return f'{section} - {name}'


@ register.filter(name='get_field_plaintext')
def get_field_plaintext(field_content, field_name) -> str:
    if field_name == 'tags':
        return _get_tags_plaintext(field_content)
    return field_content
