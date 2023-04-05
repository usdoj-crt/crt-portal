import urllib.parse
from django import template
from django.http import QueryDict

register = template.Library()


@register.simple_tag
def back_to_all(return_url_args=''):
    parsed_args = urllib.parse.unquote(return_url_args)
    querydict = QueryDict(parsed_args).dict()
    grouping = querydict.get('grouping', 'default')
    if grouping == 'default':
        return return_url_args
    violation_summary = querydict.get('violation_summary', '')
    if violation_summary.startswith('^') and violation_summary.endswith('$'):
        querydict.pop('violation_summary')
        return_url_args = dict_to_query(querydict)
    return return_url_args


def dict_to_query(querydict):
    query = ''
    for key in querydict.keys():
        query += str(key) + '=' + str(querydict[key]) + "&"
    return query
