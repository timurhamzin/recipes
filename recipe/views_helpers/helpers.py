from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from recipe.models import Recipe


@login_required
def serve_shopping_list(request):
    user = request.user
    purchased_ids = list(user.purchased.values_list('recipe', flat=True))
    ingredients = {}
    purchased = Recipe.objects.filter(id__in=purchased_ids).prefetch_related(
        'recipeingridient_set', 'recipeingridient_set__ingridient').all()
    for recipe in purchased:
        for ri in recipe.recipeingridient_set.all():
            key = f'{ri.ingridient.title} ({ri.ingridient.measurement_unit})'
            ingredients[key] = ingredients.get(key, 0) + ri.amount
    file_data = '\n'.join(f'{k} - {v}' for k, v in ingredients.items())
    response = HttpResponse(file_data,
                            content_type='application/text charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
    return response
