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
    'contact_first_name': '__contains',
    'contact_last_name': '__contains',
    'contact_email': '__search',
    'other_class': '__search',
    'violation_summary': '__search',
    'location_name': '__search',
    'location_city_town': '__contains',
    'location_address_line_1': '__search',
    'location_address_line_2': '__search',
    'create_date_start': '__gte',
    'create_date_end': '__lte',
    'public_id': '__contains',
    'primary_statute': '__in',
    'assigned_to': 'foreign_key',
    'summary': 'summary',
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
            elif filter_options[field] == '__contains':
                kwargs[f'{field}__icontains'] = request.GET.getlist(field)[0]
            elif field.startswith('create_date'):
                # filters by a start date or an end date expects ddmmyyyy
                year = int(request.GET.getlist(field)[0][:4])
                month = int(request.GET.getlist(field)[0][4:6])
                day = int(request.GET.getlist(field)[0][6:])
                kwargs[f'create_date{filter_options[field]}'] = datetime.date(year, month, day)
            elif filter_options[field] == 'summary':
                # assumes summaries are edited so there is only one per report - that is current behavior
                kwargs['internal_comments__note__search'] = request.GET.getlist(field)[0]
                kwargs['internal_comments__is_summary'] = True
            elif filter_options[field] == 'foreign_key':
                # assumes assigned_to but could add logic for other foreign keys in the future
                kwargs['assigned_to__username__in'] = request.GET.getlist(field)

    # returns a filtered query, and a dictionary that we can use to keep track of the filters we apply
    return Report.objects.filter(**kwargs), filters
