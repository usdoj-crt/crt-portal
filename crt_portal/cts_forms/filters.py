# Class to handle filtering Reports by supplied query params,
# provided they are valid filterable model properties.
from .models import Report

# To add a new filter option for Reports, add the field name and expected filter behavior
filter_options = {
    'assigned_section': '__in',
    'primary_complaint': '__in',
    'status': '__in',
    'location_state': '__in',
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

    # returns a query and a dictionary that we can use to keep track of the filters we apply
    return Report.objects.filter(**kwargs), filters
