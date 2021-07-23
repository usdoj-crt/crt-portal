from django.db.models import F
from django.http import Http404

from .models import Report

SORT_DESC_CHAR = '-'


def _valid_sort_params(sort):
    valid_fields = [f.name for f in Report._meta.fields]
    return all(elem.replace("-", '') in valid_fields for elem in sort)


def report_sort(querydict):
    sort = querydict.getlist('sort')

    if not _valid_sort_params(sort):
        raise Http404(f'Invalid sort request: {sort}')

    sort_exprs = []
    # apply the sort items individually so that we can push nulls to the back
    for sort_item in sort:
        if sort_item[0] == SORT_DESC_CHAR:
            sort_exprs.append(F(sort_item[1::]).desc(nulls_last=True))
        else:
            sort_exprs.append(F(sort_item).asc(nulls_last=True))

    sort_exprs.extend([F('create_date').desc(), F('id').desc()])

    return sort_exprs, sort
