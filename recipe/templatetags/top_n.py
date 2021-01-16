from django import template

register = template.Library()


@register.filter
def top_n(value, n):
    return value.order_by('-pub_date')[:n]
