from django.template.defaultfilters import register
from django.http import QueryDict
from urllib.parse import urlencode

from recipe.views import DEFAULT_TAG_VALUE


@register.simple_tag
def change_tag(tag_name, get_params):
    get_dict = QueryDict(get_params).dict()
    tag_val = get_dict.get(tag_name, DEFAULT_TAG_VALUE)
    tag_val = 1 - int(tag_val)
    get_dict[tag_name] = tag_val
    return urlencode(get_dict)


@register.simple_tag
def get_tag(tag_name, get_params):
    get_dict = QueryDict(get_params).dict()
    return int(get_dict.get(tag_name, DEFAULT_TAG_VALUE))
