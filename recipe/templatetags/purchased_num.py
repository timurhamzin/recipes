from django.template.defaultfilters import register


@register.simple_tag
def purchased_num(request):
    return request.user.purchased_recipes.count()
