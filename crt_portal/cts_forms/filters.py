# Class to handle filtering Reports by supplied query params,
# provided they are valid filterable model properties.
import datetime

from .models import Report

# To add a new filter option for Reports, add the field name and expected filter behavior
filter_options = {
    'assigned_section': '__in',
    'primary_complaint': '__in',
    'status': '__in',
    'location_state': '__in',
    'primary_complaint': '__in',
    'contact_first_name': '__search',
    'contact_last_name': '__search',
    'contact_email': '__search',
    'other_class': '__search',
    'violation_summary': '__search',
    'location_name': '__search',
    'location_address_line_1': '__search',
    'location_address_line_2': '__search',
    'create_date_start': '__gte',
    'create_date_end': '__lte',
}


# Populate query with valid filterable fields
def report_filter(request):
    kwargs = {}
    filters = {}
    for field in filter_options.keys():
        filter_list = request.GET.getlist(field)
        if len(filter_list) > 0:
            filters[field] = request.GET.getlist(field)
            if filter_options[field] == '__in':
                # works for one or more options with exact matches
                kwargs[f'{field}__in'] = request.GET.getlist(field)
            elif filter_options[field] == '__search':
                # takes one phrase
                kwargs[f'{field}__search'] = request.GET.getlist(field)[0]
            elif field.startswith('create_date'):
                # filters by a start date or an end date expects ddmmyyyy
                year = int(request.GET.getlist(field)[0][:4])
                month = int(request.GET.getlist(field)[0][4:6])
                day = int(request.GET.getlist(field)[0][6:])
                kwargs[f'create_date{filter_options[field]}'] = datetime.date(year, month, day)

    # returns keyword arguments that will be used for filtering, and a dictionary that we can use to keep track of the filters we apply
    return kwargs, filters
