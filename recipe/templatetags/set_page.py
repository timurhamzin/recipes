from django.template.defaultfilters import register
from django.http import QueryDict
from urllib.parse import urlencode


@register.simple_tag
def set_page(page, get_params, add_to_page=0):
    get_dict = QueryDict(get_params).dict()
    get_dict['page'] = int(page) + int(add_to_page)
    return urlencode(get_dict)
