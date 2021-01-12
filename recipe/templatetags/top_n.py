from django import template

register = template.Library()

@register.filter
def top_n(value, n):
    return value[:n]
