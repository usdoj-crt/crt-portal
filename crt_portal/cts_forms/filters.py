# Class to handle filtering Reports by supplied query params,
# provided they are valid filterable model properties.
import re
import urllib.parse
from datetime import datetime

from django.contrib.postgres.search import SearchQuery
from django.db import connection

from utils.datetime_fns import change_datetime_to_end_of_day

from .models import Report, User
from actstream import registry
from actstream.models import actor_stream

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
    'contact_phone': 'contact_phone',

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
                    dateObj = change_datetime_to_end_of_day(dateObj, field)
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
                if querydict.getlist(field)[0] == '(none)':
                    kwargs['assigned_to__isnull'] = True
                else:
                    kwargs['assigned_to__username__in'] = querydict.getlist(field)
            elif filter_options[field] == 'eq':
                kwargs[field] = querydict.getlist(field)[0]
            elif filter_options[field] == '__gte':
                kwargs[field] = querydict.getlist(field)
            elif filter_options[field] == 'violation_summary':
                search_query = querydict.getlist(field)[0]
                qs = qs.filter(violation_summary_search_vector=_make_search_query(search_query))
            elif filter_options[field] == 'contact_phone':
                # Removes all non digit characters, then breaks the number into blocks to search individually
                # EG (123) 456-7890 will search to see if  "123" AND "456" AND "7890" are in the number
                phone_number_array = ''.join(c if c.isdigit() else ' ' for c in querydict.getlist(field)[0]).split()
                for number_block in phone_number_array:
                    qs = qs.filter(contact_phone__icontains=number_block)

    # Check to see if there are multiple values in report_reason search and run distinct if so.  If not, run a regular
    # much faster search.
    if len(kwargs.get('protected_class__value__in', [])) > 1:
        qs = qs.filter(**kwargs).distinct()
    else:
        qs = qs.filter(**kwargs)
    return qs, filters


def dashboard_filter(querydict):
    kwargs = {}
    filters = {}
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
                    dateObj = change_datetime_to_end_of_day(dateObj, field)
                    kwargs[f'{field_name}{filter_options[field]}'] = dateObj
                except ValueError:
                    # if the date is invalid, we ignore it.
                    continue

    registry.register(User)
    selected_actor_username = querydict.get("assigned_to", None)
    selected_actor = User.objects.filter(username=selected_actor_username).first()
    if selected_actor:
        filtered_actions = actor_stream(selected_actor).filter(**kwargs)
    else:
        return filters, []
    return filters, filtered_actions


def _make_search_query(search_text):
    # Websearch will drop parentheses from query. So if a set of parentheses is
    # detected, we attempt to convert it to a tsquery
    if '(' in search_text and ')' in search_text:
        search_text = search_text.replace(' AND ', ' & ')
        search_text = search_text.replace(' OR ', ' | ')
        search_text = search_text.replace(' -', ' !')
        # In between search tokens that don't have operators, insert &
        # e.g. "foo -(bar | baz qux)" => "foo & !(bar | baz & qux)"
        search_text = re.sub('([a-zA-Z)"]) ([a-zA-Z("!])', r'\1 & \2', search_text)
        # Note: the only search type we don't handle here are exact phrase quotes.
        with connection.cursor() as cursor:
            try:
                # This can still create syntax errors, so we ask the db to validate the
                # query for us. This query only parses the input, it doesn't incur the
                # performance hit of executing the search twice. If the query isn't
                # valid, we catch the error and execute a websearch instead, which is
                # more forgiving with syntax errors.
                cursor.execute("SELECT to_tsquery('english', %s);", [search_text])
                query = SearchQuery(search_text, config='english', search_type='raw')
            except Exception:  # catch *all* exceptions
                query = SearchQuery(search_text, config='english', search_type='websearch')
    else:
        query = SearchQuery(search_text, config='english', search_type='websearch')

    return query
