from django.template.defaultfilters import register


@register.simple_tag
def subtract(a, b):
    return a - b
