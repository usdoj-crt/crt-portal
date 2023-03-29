from django import template

register = template.Library()


@register.simple_tag
def grouping_page(page_args=[], group_params=[], index=0, page_number=1):
    group_params_copy = group_params.copy()
    group_params_copy[index] = group_params_copy[index].copy()
    group_params_copy[index]['page'] = page_number
    return f'{page_args}&group_params={group_params_copy}'
