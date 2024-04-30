# Class to handle filtering Reports by supplied query params,
# provided they are valid filterable model properties.
from typing import Tuple, Dict, Any

import re
import urllib.parse
from datetime import datetime, timedelta
from operator import and_

from django.apps import apps

from django.db.models import Q, ExpressionWrapper, Count, IntegerField, Min, F, Value, CharField, DateField, Func
from django.db.models.functions import ExtractYear, Concat, Cast, Left

from django.contrib.postgres.search import SearchQuery, TrigramSimilarity
from django.db import connection
from django.db.models.lookups import GreaterThan, LessThanOrEqual
from django.http.request import QueryDict, MultiValueDict

from utils.datetime_fns import change_datetime_to_end_of_day
from utils.request_utils import get_user_section

from .models import Report, User
from actstream import registry
from actstream.models import actor_stream, Action

Feature = apps.get_model('features', 'Feature')

foreign_key_displays = {
    'assigned_to': ('username', str),
    'origination_utm_campaign': ('internal_name', str),
    'retention_schedule': ('name', str),
    'tags': ('id', int),
}

# To add a new filter option for Reports, add the field name and expected filter behavior
# These filters should match the order they're presented in filter-controls.html
filter_options = {
    'actions': '__in',
    'assigned_section': '__in',
    'status': '__in',
    'contact_first_name': '__icontains',
    'contact_last_name': '__icontains',
    'public_id': '__icontains',  # aka "ID" or "Complaint ID"
    'assigned_to': 'foreign_key',  # aka "Assignee"
    'origination_utm_campaign': 'foreign_key',
    'tags': 'foreign_key',
    'litigation_hold': 'eq',
    'location_address_line_1': '__icontains',  # not in filter controls?
    'location_address_line_2': '__icontains',  # not in filter controls?
    'location_city_town': '__icontains',
    'location_state': '__in',
    'retention_schedule': 'foreign_key',

    'contact_email': '__icontains',
    'contact_phone': 'contact_phone',

    'create_date_start': '__gte',
    'create_date_end': '__lte',
    'closed_date_start': '__gte',  # not in filter controls?
    'closed_date_end': '__lte',  # not in filter controls?
    'modified_date_start': '__gte',  # not in filter controls?
    'modified_date_end': '__lte',  # not in filter controls?

    'primary_statute': '__in',  # aka "Classification"
    'district': '__in',
    'primary_complaint': '__in',  # aka "Primary issue"
    'dj_number': 'dj_number',
    'reported_reason': 'reported_reason',

    # "Relevant details":
    'commercial_or_public_place': '__in',
    'public_or_private_employer': '__in',
    'employer_size': '__in',
    'public_or_private_school': '__in',
    'inside_correctional_facility': '__in',
    'correctional_facility_type': '__in',

    'servicemember': 'eq',
    'intake_format': '__in',
    'referred': 'eq',  # aka "Secondary review"
    'language': '__in',  # aka "Report language"
    'hate_crime': 'eq',

    'violation_summary': 'violation_summary',  # aka "Personal description"
    'summary': 'summary',  # aka "CRT summary"
    'location_name': 'fuzzy',
    'other_class': '__search',  # not in filter controls?
    'disposition_status': 'disposition_status',
    'expiration_date': 'expiration_date',
    # this is not a db query filter, not needed here, duplicate tag fix, removed from the filter tag list
    # 'per_page': '__pass',  # adding so a filter tag will show up in /form/view.  No filtering will actually happen.
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


def report_grouping(querydict):
    all_qs, filters = report_filter(querydict)
    groups = all_qs.values('violation_summary').annotate(
        total=Count('violation_summary'),
        first_report_id=Min('pk'),
    ).filter(total__gt=1).order_by('-total')
    group_queries = []
    summaries = []
    for group in groups:
        description = group['violation_summary']
        if description == "":
            continue
        desc = description
        summaries.append(description)
        group_queries.append({
            "qs": all_qs.filter(violation_summary=description),
            "desc": desc,
            "desc_id": group['first_report_id'],
        })
    group_queries.append({
        "qs": all_qs.exclude(violation_summary__in=summaries),
        "desc": "All other reports",
        "desc_id": -1,
    })
    return group_queries, filters


def get_report_filter_from_search(search):
    querydict = QueryDict('', mutable=True)
    querydict.update(MultiValueDict(urllib.parse.parse_qs(search.query)))
    return report_filter(querydict)


def _get_fuzzy_kwargs(field, querydict) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    query = querydict.getlist(field)[0]

    if not Feature.is_feature_enabled('fuzzy-location-name'):
        exact_match = {f'{field}__icontains': query}, {}, {}
        return exact_match

    filters = {}
    try:
        soundslike = int(querydict.getlist(f'{field}_1')[0])
        filters[f'{field}_1'] = [soundslike]
    except (IndexError, ValueError):
        soundslike = 0
    try:
        lookslike = int(querydict.getlist(f'{field}_2')[0])
        filters[f'{field}_2'] = [lookslike]
    except (IndexError, ValueError):
        lookslike = 0

    # This is for backwards compatibility to support the old fuzzy search syntax.
    if query.startswith('~'):
        if not soundslike and not lookslike:
            lookslike = 3
            soundslike = 3
        query = query[1:]

    return {}, {field: {'query': query,
                        'soundslike': soundslike,
                        'lookslike': lookslike}}, filters


def report_filter(querydict):
    kwargs = {}
    filters = {}
    fuzzy = {}
    qs = Report.objects.filter()
    for field in filter_options.keys():
        filter_list = querydict.getlist(field)

        field_options = filter_options[field]
        if len(filter_list) <= 0:
            continue

        filters[field] = querydict.getlist(field)
        if field_options == '__in':
            # works for one or more options with exact matches
            kwargs[f'{field}__in'] = querydict.getlist(field)
        elif field_options == '__search':
            # takes one phrase
            kwargs[f'{field}__search'] = querydict.getlist(field)[0]
        elif field_options == '__icontains':
            kwargs[f'{field}__icontains'] = querydict.getlist(field)[0]
        elif 'date' in field and field_options != 'expiration_date':
            # filters by a start date or an end date expects yyyy-mm-dd
            field_name = _get_date_field_from_param(field)
            encodedDate = querydict.getlist(field)[0]
            decodedDate = urllib.parse.unquote(encodedDate)
            try:
                dateObj = datetime.strptime(decodedDate, "%Y-%m-%d")
                dateObj = change_datetime_to_end_of_day(dateObj, field)
                kwargs[f'{field_name}{field_options}'] = dateObj
            except ValueError:
                # if the date is invalid, we ignore it.
                continue
        elif field_options == 'summary':
            # assumes summaries are edited so there is only one per report - that is current behavior
            kwargs['internal_comments__note__search'] = querydict.getlist(field)[0]
            kwargs['internal_comments__is_summary'] = True
        elif field_options == 'reported_reason':
            reasons = querydict.getlist(field)
            kwargs['protected_class__value__in'] = reasons
        elif field_options == 'dj_number':
            dj_number = querydict.get(field, None)
            if dj_number is None:
                continue
            statute, district, sequence = dj_number.rsplit('-', 2)
            statute = statute or '[^-]+(-USE)?'
            district = district or '[^-]+'
            sequence = sequence or '[^-]+'
            kwargs['dj_number__iregex'] = f'^{statute}-{district}-{sequence}$'
        elif field_options == 'foreign_key':
            display_field, cast = foreign_key_displays[field]
            if querydict.getlist(field)[0] == '(none)':
                kwargs[f'{field}__isnull'] = True
            else:
                values = [cast(v) for v in querydict.getlist(field)]
                kwargs[f'{field}__{display_field}__in'] = values
        elif field_options == 'eq':
            kwargs[field] = querydict.getlist(field)[0]
        elif field_options == '__gte':
            kwargs[field] = querydict.getlist(field)
        elif field_options == 'fuzzy':
            field_kwargs, field_similarity, field_filters = _get_fuzzy_kwargs(field, querydict)
            kwargs.update(field_kwargs)
            fuzzy.update(field_similarity)
            filters.update(field_filters)
        elif field_options == 'violation_summary':
            search_query = querydict.getlist(field)[0]
            if search_query.startswith('^#') and search_query.endswith('$'):
                report_id = search_query[2:-1]
                if report_id == '-1':
                    continue  # This means "all other reports" when grouping
                try:
                    report = Report.objects.get(pk=report_id)
                    qs = qs.filter(violation_summary=report.violation_summary)
                except (Report.DoesNotExist, ValueError):
                    # This might not be a report id (for example, hashtags):
                    qs = qs.filter(violation_summary=search_query[1:-1])
            elif search_query.startswith('^') and search_query.endswith('$'):
                # Allow for "exact match" using the common regex syntax.
                qs = qs.filter(violation_summary=search_query[1:-1])
            else:
                qs = qs.filter(violation_summary_search_vector=_make_search_query(search_query))
        elif field_options == 'contact_phone':
            # Removes all non digit characters, then breaks the number into blocks to search individually
            # EG (123) 456-7890 will search to see if  "123" AND "456" AND "7890" are in the number
            phone_number_array = ''.join(c if c.isdigit() else ' ' for c in querydict.getlist(field)[0]).split()
            for number_block in phone_number_array:
                qs = qs.filter(contact_phone__icontains=number_block)
        elif field_options in ['disposition_status', 'expiration_date']:
            qs = qs.filter(~Q(retention_schedule__retention_years=0), closed_date__isnull=False, batched_for_disposal=False)
            user_section = get_user_section()
            if user_section:
                qs = qs.filter(assigned_section=user_section)
            qs = qs.annotate(retention_year=F('retention_schedule__retention_years'),
                             expiration_year=F('retention_year') + ExtractYear('closed_date') + 1,
                             expiration_date=Cast(Concat(F('expiration_year'), Value('-'), Value('01'), Value('-'), Value('01'), output_field=CharField()), output_field=DateField()),
                             eligible_date=ExpressionWrapper(F('expiration_date') - timedelta(days=30), output_field=DateField()))
            if field_options == 'expiration_date':
                expiration_date = querydict.getlist(field)[0]
                expiration_datetime = change_datetime_to_end_of_day(datetime.strptime(expiration_date, '%Y-%m-%d'), field)
                kwargs['expiration_date'] = expiration_datetime

            if field_options == 'disposition_status' and 'expiration_date' not in querydict:
                today = datetime.today().date()
                disposition_status = querydict.getlist(field)[0]
                if disposition_status == 'past':
                    kwargs['expiration_date__lt'] = today
                if disposition_status == 'eligible':
                    kwargs['expiration_date__gte'] = today
                    kwargs['eligible_date__lte'] = today
                if disposition_status == 'other':
                    kwargs['eligible_date__gt'] = today

    # Check to see if there are multiple values in report_reason search and run distinct if so.  If not, run a regular
    # much faster search.
    if len(kwargs.get('protected_class__value__in', [])) > 1:
        qs = qs.filter(**kwargs).distinct()
    else:
        qs = qs.filter(**kwargs)
    for field_name, kwargs in fuzzy.items():
        qs = filter_by_similar(qs, field_name, **kwargs)
    return qs, filters


def dashboard_filter(querydict):
    kwargs = {}
    filters = {}
    for field in filter_options.keys():
        filter_list = querydict.getlist(field)
        if len(filter_list) > 0:
            filters[field] = querydict.getlist(field)
            if field == 'actions':
                field_name = 'verb'
                kwargs[f'{field_name}__in'] = querydict.getlist(field)
            if field == 'public_id':
                field_name = 'target_object_id'
                kwargs[f'{field_name}__icontains'] = querydict.getlist(field)[0]
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
        response_actions = filtered_actions.filter(verb='Contacted complainant:')
    else:
        return filters, Action.objects.none(), Action.objects.none()
    return filters, filtered_actions, response_actions


class Metaphone(Func):
    function = 'METAPHONE'
    arity = 2
    output_field = CharField()


class LevenshteinLessEqual(Func):
    function = 'levenshtein_less_equal'
    arity = 3
    output_field = IntegerField()


class OctetLength(Func):
    function = 'octet_length'
    arity = 1
    output_field = IntegerField()


def filter_by_similar(queryset, column, *, query, soundslike, lookslike):
    target = Left(column, 255)
    soundslike = int(soundslike)
    lookslike = int(lookslike)

    soundslike_filter = GreaterThan(
        TrigramSimilarity(
            Metaphone(target, 255),
            Metaphone(Value(query), 255),
        ),
        1.0 - (soundslike / 10.0),
    )

    # Normalize the distance based on the word size:
    distance = min(int((lookslike / 10.0) * len(query)), 255)
    lookslike_filter = LessThanOrEqual(
        LevenshteinLessEqual(
            target,
            Value(query),
            Value(distance),
        ),
        distance
    )

    is_similar = Q(**{f'{column}__icontains': query})
    if soundslike:
        is_similar |= soundslike_filter
    if lookslike:
        is_similar |= lookslike_filter

    # Fuzzy match functions only support 255 bytes.
    # Some characters take up more than a byte.
    # There's no good way to truncate by byte, so we filter these out.
    return queryset.annotate(
        **{f'{column}_similar': and_(
            LessThanOrEqual(
                OctetLength(target),
                255,
            ),
            is_similar,
        )}
    ).filter(**{f'{column}_similar': True})


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
