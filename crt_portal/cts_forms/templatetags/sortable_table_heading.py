import json
from django import template


register = template.Library()
sort_lookup = {
    'status': 'status',
    'total #': 'email_count',
    'id': 'public_id',
    'routed': 'assigned_section',
    'submitted': 'create_date',
    'contact name': 'contact_last_name',
    'location name': 'location_name',
    'incident location': 'location_city_town',
    'incident date': 'last_incident_month',
    'timestamp': 'timestamp',
    'action': 'actions',
    'detail': 'detail',
}
sortable_props = [
    'status',
    'email_count',
    'public_id',
    'assigned_section',
    'create_date',
    'contact_last_name',
    'location_name',
    'location_city_town',
    'last_incident_month',
    'timestamp',
    'actions',
    'detail',
]


# Resolve the table heading names to the names of the sortable model properties
def heading_2_model_prop(heading):
    if heading == 'contact name':
        return ['contact_last_name', 'contact_first_name']
    elif heading == 'incident location':
        return ['location_city_town', 'location_state']
    elif heading == 'incident date':
        return ['last_incident_day', 'last_incident_month', 'last_incident_year']
    else:
        return [sort_lookup[heading]]


# Helper function to generate a sort query string to be passed to the template
# When the query is descending, returns a query string for an ascending sort.
def sort_url_factory(heading, is_descending, filter_state, grouping, group_params, index):
    sort_properties = heading_2_model_prop(heading)

    if is_descending:
        sortables = sort_properties
    else:
        sortables = map(lambda x: '-{}'.format(x), sort_properties)
    if not group_params:
        return '?' + '&'.join('sort=' + p for p in sortables) + '&grouping=' + grouping + filter_state
    group_params_copy = group_params.copy()
    group_params_copy[index] = group_params_copy[index].copy()
    group_params_copy[index]['sort'] = [''.join(p for p in sortables)]
    # Go back to page 1 of results when sort params change
    group_params_copy[index]['page'] = 1
    group_params_copy = json.dumps(group_params_copy)
    return f'?group_params={group_params_copy}&grouping={grouping}{filter_state}'


@register.inclusion_tag('forms/snippets/sortable_table_heading.html')
def render_sortable_heading(heading, sort_state, filter_state, grouping='default', group_params=None, index=1, nowrap=False):
    safe_heading = heading.lower()
    sortable_prop = sort_lookup.get(safe_heading, None)

    sort_dict = {
        'heading': heading,
        'id': heading.lower().replace(' ', '-') + '-sort',
        'nowrap': nowrap
    }
    if sortable_prop in sortable_props:
        is_descending = sort_state.get(sortable_prop, False)
        sort_dict.update({
            'sort_url': sort_url_factory(safe_heading, is_descending, filter_state, grouping, group_params, index),
            'is_descending': is_descending
        })

    return sort_dict
