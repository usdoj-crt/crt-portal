from django.db.models import F
from django.http import Http404
from actstream.models import actor_stream

from .models import EmailReportCount, Report

SORT_DESC_CHAR = '-'


def _valid_sort_params(sort, type):
    if type == 'activity':
        valid_fields = ['timestamp', 'verb', 'description', 'target_object_id']
    else:
        valid_fields = [f.name for f in Report._meta.fields] + [f.name for f in EmailReportCount._meta.fields]
    return all(elem.replace("-", '') in valid_fields for elem in sort)


def report_sort(sort):

    if not _valid_sort_params(sort, 'report'):
        raise Http404(f'Invalid sort request: {sort}')

    sort_exprs = []
    # apply the sort items individually so that we can push nulls to the back
    for sort_item in sort:
        nulls_last = 'email_count' in sort_item
        if sort_item[0] == SORT_DESC_CHAR:
            sort_exprs.append(F(sort_item[1::]).desc(nulls_last=nulls_last))
        else:
            sort_exprs.append(F(sort_item).asc(nulls_last=nulls_last))

    sort_exprs.extend([F('create_date').desc(), F('id').desc()])

    return sort_exprs, sort


def activity_sort(sort):

    if not _valid_sort_params(sort, 'activity'):
        raise Http404(f'Invalid sort request: {sort}')

    sort_exprs = []

    for sort_item in sort:
        sort_name = sort_item
        if sort_item == 'actions':
            sort_name = 'verb'
        if sort_item[0] == SORT_DESC_CHAR:
            sort_exprs.append(F(sort_item[1::]))
        else:
            sort_exprs.append(F(sort_item))

    sort_exprs.extend([F('id').desc()])

    return sort_exprs, sort
