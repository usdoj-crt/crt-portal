from django import template


register = template.Library()
sort_lookup = {
    'status': 'status',
    'routed': 'assigned_section',
    'submitted': 'create_date',
    'contact name': 'contact_last_name'
}
sortable_props = [
    'status', 'assigned_section', 'create_date', 'contact_last_name'
]


# Resolve the table heading names to the names of the sortable model properties
def heading_2_model_prop(heading):
    if heading == 'contact name':
        return ['contact_last_name', 'contact_first_name']
    else:
        return [sort_lookup[heading]]


# Helper function to generate a sort query string to be passed to the template
# When the query is descending, returns a query string for an ascending sort.
def sort_url_factory(heading, is_descending):
    sort_properties = heading_2_model_prop(heading)

    if is_descending:
        sortables = sort_properties
    else:
        sortables = map(lambda x: '-{}'.format(x), sort_properties)

    return '?' + '&'.join('sort=' + p for p in sortables)


@register.inclusion_tag('forms/snippets/sortable_table_heading.html')
def render_sortable_heading(heading, sort_state):
    safe_heading = heading.lower()
    sortable_prop = sort_lookup.get(safe_heading, None)

    sort_dict = {
        'heading': heading
    }

    if sortable_prop in sortable_props:
        is_descending = sort_state.get(sortable_prop, False)
        sort_dict.update({
            'sort_url': sort_url_factory(safe_heading, is_descending),
            'is_descending': is_descending
        })

    return sort_dict
