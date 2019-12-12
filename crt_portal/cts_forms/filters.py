# Class to handle filtering Reports by supplied query params,
# provided they are valid filterable model properties.
from .models import Report

# To add a new filter option for Reports, add the field name and expected filter behavior
filter_options = {
    'assigned_section': 'match',
    'primary_complaint': 'match',
    'status': 'match',
    'location_state': 'match',
}

# Populate query with valid filterable fields
def report_filter(request):
    kwargs = {}
    filters = {}
    for field in filter_options.keys():
        if filter_options[field] == 'match':
            filter_list = request.GET.getlist(field)
            if len(filter_list) > 0:
                # works for one or more options with exact matches
                kwargs[f'{field}__in'] = request.GET.getlist(field)
                filters[field] = request.GET.getlist(field)

    # returns a query and a dictionary that we can use to keep track of the filters we apply
    return Report.objects.filter(**kwargs), filters
