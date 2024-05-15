from django.db.models import F

from .models import EmailReportCount, Report

SORT_DESC_CHAR = '-'


def _valid_sort_params(sort, type):
    if type == 'activity':
        valid_fields = ['timestamp', 'verb', 'description', 'target_object_id']
    elif type == 'saved_search':
        valid_fields = ['created_by', 'section', 'name']
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
        # Simply reset the sort if the params are not valid:
        return [], []

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
        # Simply reset the sort if the params are not valid:
        return [], []

    sort_exprs = []

    for sort_item in sort:
        if sort_item[0] == SORT_DESC_CHAR:
            sort_exprs.append(F(sort_item[1::]))
        else:
            sort_exprs.append(F(sort_item))
    sort_exprs.extend([F('pk').desc()])

    return sort_exprs, sort
