from django.template.defaultfilters import register


@register.simple_tag
def user_follows(user):
    author_ids = list(user.follows.values_list('author', flat=True))
    return author_ids
