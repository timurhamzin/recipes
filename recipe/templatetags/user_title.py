from django import template

register = template.Library()


@register.filter
def user_title(user):
    if user.first_name:
        return user.first_name
    return user.username
