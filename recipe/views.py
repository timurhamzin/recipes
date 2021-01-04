from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from recipe.models import Recipe

User = get_user_model()

CARDS_PER_PAGE = 1


def index(request):
    user = request.user
    recipes = Recipe.objects.all()
    paginator = Paginator(recipes, CARDS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    if user.is_authenticated:
        template = 'indexAuth.html'
    else:
        template = 'indexNotAuth.html'
    return render(
        request, template,
        {
            'page': page,
            'paginator': paginator,
            'recipes': recipes
        },
    )
