from django.template.defaultfilters import register


@register.simple_tag
def in_list(val, vals):
    return val in vals
