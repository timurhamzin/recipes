from django.template.defaultfilters import register
from django.utils.html import mark_safe


@register.simple_tag
def nav_item_li(request, href, text, closing_li=True, add_class=''):
    active_class = ''
    closing_li_tag = ''
    if request.path == href:
        active_class = 'nav__item_active'
    if closing_li:
        closing_li_tag = '</li>'
    return mark_safe(f'<li class="nav__item {active_class} {add_class}">'
                     f'<a href="{href}" '
                     f'class="nav__link link">{text}</a>{closing_li_tag}')
