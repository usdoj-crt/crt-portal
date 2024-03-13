from django.db.models import F
from django.http import Http404

from .models import EmailReportCount, Report

SORT_DESC_CHAR = '-'


def _valid_sort_params(sort, type):
    if type == 'activity':
        valid_fields = ['timestamp', 'verb', 'description', 'target_object_id']
    elif type == 'batch':
        valid_fields = ['status', 'retention_schedule', 'proposed_disposal_date', 'create_date']
    else:
        fields = [
            *EmailReportCount._meta.fields,
            *Report._meta.fields,
        ]
        valid_fields = [f.name for f in fields]
        valid_fields.append('expiration_date')
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


def other_sort(sort, sort_type):

    if not _valid_sort_params(sort, sort_type):
        raise Http404(f'Invalid sort request: {sort}')

    sort_exprs = []

    for sort_item in sort:
        if sort_item[0] == SORT_DESC_CHAR:
            sort_exprs.append(F(sort_item[1::]))
        else:
            sort_exprs.append(F(sort_item))
    if sort_type == 'batch':
        sort_exprs.extend([F('uuid').desc()])
    else:
        sort_exprs.extend([F('id').desc()])

    return sort_exprs, sort
