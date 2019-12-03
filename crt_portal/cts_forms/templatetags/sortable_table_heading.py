from django import template


register = template.Library()
sort_lookup = {
  'status': 'status',
  'routed': 'assigned_section',
  'submitted': 'create_date',
  'contact_name': 'contact_last+_name'
}

def heading_2_model_prop(heading):
    if heading == 'contact name':
        return ('contact_last_name', 'contact_first_name')
    else:
      return (sort_lookup[heading])

def sort_url_factory(heading):
    sort_properties = heading_2_model_prop(heading)
    descending = '-{}'.format(sort_lookup[heading])
    
    if is_descending:
        sortables = map(lambda x: '-{}'.format(x), sort_properties)
    else:
        sortables = sort_properties

    return '?' + '&'.join('sort='+p for p in sortables)

@register.inclusion_tag('snippets/sortable_table_heading.html')
def render_sortable_heading(heading, sort_state):
    
    return None
    # is_descending = 
    # # this field is treated differently as it contains
    # # both a first and last name to sort against.
    # is_contact_name = heading == 'contact_name'
    # sort_url = if is_contact_name and 

    # if username:
    #     menu_user = username
    # elif recent_users:
    #     # sorted here could be replaced by min or QuerySet method, it depends
    #     # for example: 
    #     # menu_user = min(recent_users, key=lambda u:u.timestamp).username
    #     menu_user = sorted(recent_users)[0]['username']
    # return {'menu_user':menu_user}

# # in template, it looks like
# {% render_menu username recent_users %}