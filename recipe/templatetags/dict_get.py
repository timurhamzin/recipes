from django.template.defaultfilters import register


@register.simple_tag
def dict_get(dict, key, default=''):
    return dict.get(key, default)


@register.simple_tag
def join_strings(strings, separator):
    if strings:
        return separator.join(strings)
