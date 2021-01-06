from django.template.defaultfilters import register


@register.simple_tag
def define(val=None):
    return val
