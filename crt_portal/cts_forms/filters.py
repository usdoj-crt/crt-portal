# Class to handle filtering Reports by supplied query params,
# provided they are valid filterable model properties.
import logging
import urllib.parse
from datetime import datetime

from django.contrib.postgres.search import SearchQuery, SearchVector

from .models import Report

logger = logging.getLogger(__name__)

# To add a new filter option for Reports, add the field name and expected filter behavior
filter_options = {
    'assigned_section': '__in',
    'primary_complaint': '__in',  # TODO rename to primary_issue
    'status': '__in',
    'location_state': '__in',
    'contact_first_name': '__contains',
    'contact_last_name': '__contains',
    'contact_email': '__search',
    'other_class': '__search',
    'violation_summary': 'violation_summary',
    'location_name': '__contains',
    'location_city_town': '__contains',
    'location_address_line_1': '__search',
    'location_address_line_2': '__search',
    'create_date_start': '__gte',
    'create_date_end': '__lte',
    'closed_date_start': '__gte',
    'closed_date_end': '__lte',
    'modified_date_start': '__gte',
    'modified_date_end': '__lte',
    'public_id': '__contains',
    'primary_statute': '__in',
    'assigned_to': 'foreign_key',
    'summary': 'summary',
    'servicemember': 'eq',
    'hate_crime': 'eq',
    'intake_format': '__in',  # TODO rename to intake_type
    'commercial_or_public_place': '__in',  # TODO
    'reported_reason': 'reported_reason',
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
            elif filter_options[field] == '__contains':
                kwargs[f'{field}__icontains'] = querydict.getlist(field)[0]
            elif 'date' in field:
                # filters by a start date or an end date expects yyyy-mm-dd
                field_name = _get_date_field_from_param(field)
                encodedDate = querydict.getlist(field)[0]
                decodedDate = urllib.parse.unquote(encodedDate)
                try:
                    dateObj = datetime.strptime(decodedDate, "%Y-%m-%d")
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
                kwargs['assigned_to__username__in'] = querydict.getlist(field)
            elif filter_options[field] == 'eq':
                kwargs[field] = querydict.getlist(field)[0]
            elif filter_options[field] == '__gte':
                kwargs[field] = querydict.getlist(field)
            elif filter_options[field] == 'violation_summary':
                combined_or_search = _combine_term_searches_with_or(filter_list)
                qs = qs.annotate(search=SearchVector('violation_summary')).filter(search=combined_or_search)
    qs = qs.filter(**kwargs)
    return qs, filters


def _combine_term_searches_with_or(terms):
    """Create a CombinedSearchQuery of all received search terms"""
    combined_search = SearchQuery(terms.pop())
    for term in terms:
        combined_search = combined_search | SearchQuery(term)
    return combined_search
