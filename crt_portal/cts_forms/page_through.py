from django.core.paginator import EmptyPage, PageNotAnInteger


def pagination(paginator, page, per_page):
    page = int(page)
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)

    adjacent_pages = 1

    show_first = page > adjacent_pages + 1
    first_ellipsis = show_first and not (page <= adjacent_pages + 2)

    show_last = page < paginator.num_pages - adjacent_pages
    last_ellipsis = show_last and not (page == paginator.num_pages - adjacent_pages - 1)

    start_page = max(page - adjacent_pages, 1)
    end_page = min(page + adjacent_pages + 1, paginator.num_pages + 1)

    page_numbers = [n for n in range(start_page, end_page) if n > 0]

    has_next = records.has_next()
    if has_next:
        next_page_number = records.next_page_number()
    else:
        next_page_number = 1
    has_previous = records.has_previous()
    if has_previous:
        previous_page_number = records.previous_page_number()
    else:
        previous_page_number = 1

    page_format = {
        'page': page,
        'per_page': per_page,
        'show_first': show_first,
        'first_ellipsis': first_ellipsis,
        'show_last': show_last,
        'last_ellipsis': last_ellipsis,
        'page_numbers': page_numbers,
        'count': paginator.count,
        'has_previous': has_previous,
        'has_next': has_next,
        'next_page_number': next_page_number,
        'previous_page_number': previous_page_number,
        'total_pages': paginator.num_pages,
        'page_range_start': records.start_index(),
        'page_range_end': records.end_index(),
    }

    return records, page_format
