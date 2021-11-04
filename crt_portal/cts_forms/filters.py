# Class to handle filtering Reports by supplied query params,
# provided they are valid filterable model properties.
import urllib.parse
from datetime import datetime

from django.contrib.postgres.search import SearchQuery

from .models import Report
from actstream.models import Action

# To add a new filter option for Reports, add the field name and expected filter behavior
# These filters should match the order they're presented in filter-controls.html
filter_options = {
    'assigned_section': '__in',
    'status': '__in',
    'contact_first_name': '__icontains',
    'contact_last_name': '__icontains',
    'public_id': '__icontains',  # aka "ID" or "Complaint ID"
    'assigned_to': 'foreign_key',  # aka "Assignee"

    'location_address_line_1': '__icontains',  # not in filter controls?
    'location_address_line_2': '__icontains',  # not in filter controls?
    'location_city_town': '__icontains',
    'location_state': '__in',

    'contact_email': '__icontains',

    'create_date_start': '__gte',
    'create_date_end': '__lte',
    'closed_date_start': '__gte',  # not in filter controls?
    'closed_date_end': '__lte',  # not in filter controls?
    'modified_date_start': '__gte',  # not in filter controls?
    'modified_date_end': '__lte',  # not in filter controls?

    'primary_statute': '__in',  # aka "Classification"
    'primary_complaint': '__in',  # aka "Primary issue"
    'reported_reason': 'reported_reason',
    'commercial_or_public_place': '__in',  # aka "Relevant details"

    'servicemember': 'eq',
    'intake_format': '__in',
    'referred': 'eq',  # aka "Secondary review"
    'language': '__in',  # aka "Report language"
    'hate_crime': 'eq',
    'correctional_facility_type': '__in',  # aka "Prison type"

    'violation_summary': 'violation_summary',  # aka "Personal description"
    'summary': 'summary',  # aka "CRT summary"
    'location_name': '__icontains',

    'other_class': '__search',  # not in filter controls?
}

# To add a new filter option for Reports, add the field name and expected filter behavior
# These filters should match the order they're presented in filter-controls.html
dashboard_filter_options = {
    'timestamp_start': '__gte',
    'timestamp_end': '__lte',
}


# Populate query with valid filterable fields

def _get_date_field_from_param(field):
    """
    Return model field by truncating the filter preposition
    which follows the last occurrence of `_`
    """
    return field[:field.rfind('_')]


def _change_datetime_to_end_of_day(dateObj, field):
    """
    Takes a datetime and field param to ensure an end_date
    field has time moved to end of day (23:59:59)
    """
    if 'end' in field:
        return dateObj.replace(hour=23, minute=59, second=59)
    else:
        return dateObj


def report_filter(querydict):
    kwargs = {}
    filters = {}
    qs = Report.objects.filter()
    for field in filter_options.keys():
        filter_list = querydict.getlist(field)

        if len(filter_list) > 0:
            filters[field] = querydict.getlist(field)
            if filter_options[field] == '__in':
                # works for one or more options with exact matches
                kwargs[f'{field}__in'] = querydict.getlist(field)
            elif filter_options[field] == '__search':
                # takes one phrase
                kwargs[f'{field}__search'] = querydict.getlist(field)[0]
            elif filter_options[field] == '__icontains':
                kwargs[f'{field}__icontains'] = querydict.getlist(field)[0]
            elif 'date' in field:
                # filters by a start date or an end date expects yyyy-mm-dd
                field_name = _get_date_field_from_param(field)
                encodedDate = querydict.getlist(field)[0]
                decodedDate = urllib.parse.unquote(encodedDate)
                try:
                    dateObj = datetime.strptime(decodedDate, "%Y-%m-%d")
                    dateObj = _change_datetime_to_end_of_day(dateObj, field)
                    kwargs[f'{field_name}{filter_options[field]}'] = dateObj
                except ValueError:
                    # if the date is invalid, we ignore it.
                    continue
            elif filter_options[field] == 'summary':
                # assumes summaries are edited so there is only one per report - that is current behavior
                kwargs['internal_comments__note__search'] = querydict.getlist(field)[0]
                kwargs['internal_comments__is_summary'] = True
            elif filter_options[field] == 'reported_reason':
                reasons = querydict.getlist(field)
                kwargs['protected_class__value__in'] = reasons
            elif filter_options[field] == 'foreign_key':
                # assumes assigned_to but could add logic for other foreign keys in the future
                if querydict.getlist(field)[0] == '(unassigned)':
                    kwargs['assigned_to__isnull'] = True
                else:
                    kwargs['assigned_to__username__in'] = querydict.getlist(field)
            elif filter_options[field] == 'eq':
                kwargs[field] = querydict.getlist(field)[0]
            elif filter_options[field] == '__gte':
                kwargs[field] = querydict.getlist(field)
            elif filter_options[field] == 'violation_summary':
                combined_or_list = []
                for vs_filter in filter_list:
                    combined_or_list += vs_filter.split(" OR ")
                combined_or_search = _combine_term_searches_with_or(combined_or_list)
                qs = qs.filter(violation_summary_search_vector=combined_or_search)
    qs = qs.filter(**kwargs)
    return qs, filters


def dashboard_filter(querydict):
    kwargs = {}
    filters = {}
    selected_actions = []
    selected_actor = querydict.get("assigned_to", None)
    for field in filter_options.keys():
        filter_list = querydict.getlist(field)
        if len(filter_list) > 0:
            filters[field] = querydict.getlist(field)
            if 'date' in field:
                # filters by a start date or an end date expects yyyy-mm-dd
                field_name = 'timestamp'
                encodedDate = querydict.getlist(field)[0]
                decodedDate = urllib.parse.unquote(encodedDate)
                try:
                    dateObj = datetime.strptime(decodedDate, "%Y-%m-%d")
                    dateObj = _change_datetime_to_end_of_day(dateObj, field)
                    kwargs[f'{field_name}{filter_options[field]}'] = dateObj
                except ValueError:
                    # if the date is invalid, we ignore it.
                    continue
    actions = Action.objects.filter(**kwargs)
    for action in actions:
        if hasattr(action.actor, 'username') and selected_actor == action.actor.username:
            selected_actions.append(action)
    return filters, selected_actions


def _combine_term_searches_with_or(terms):
    """Create a CombinedSearchQuery of all received search terms"""
    combined_search = SearchQuery(terms.pop(), config='english')
    for term in terms:
        combined_search = combined_search | SearchQuery(term, config='english')

    return combined_search
