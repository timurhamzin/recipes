import json
from typing import Type

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Model
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from recipe.models import Recipe, Tag, RecipeIngridient, FollowRecipe, \
    Ingridient
from recipe.serializers import RecipeSerializer

User = get_user_model()

CARDS_PER_PAGE = 1
DEFAULT_TAG_VALUE = 1


def get_object_or_None(model: Type[Model], **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def index(request):
    user = request.user
    get_dict = request.GET.dict()
    all_tags = Tag.objects.all()
    selected_tags = [t.name for t in all_tags if \
                     get_dict.get(t.name, str(DEFAULT_TAG_VALUE)) == '1']
    recipes = Recipe.objects.filter(tag__name__in=selected_tags).distinct()

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
            'recipes': recipes,
            'all_tags': all_tags,
            'tag_filters': {},
        },
    )


def single_page(request, recipe_id):
    user = request.user
    recipe = get_object_or_404(Recipe, id=recipe_id)
    favorite = False
    if user.is_authenticated:
        template = 'singlePage.html'
        follow_data = dict(user=user.id, recipe=recipe_id)
        follow_obj = get_object_or_None(FollowRecipe, **follow_data)
        favorite = follow_obj is not None
    else:
        template = 'singlePageNotAuth.html'

    recipe_ingredients = RecipeIngridient.objects.filter(
        recipe=recipe_id)
    # recipe=recipe_id,
    # ingridient__in=recipe.ingridients.all().values_list('id', flat=True))
    return render(
        request, template,
        {
            'recipe': recipe,
            'tags': recipe.tag.all(),
            'recipe_ingredients': recipe_ingredients,
            'favorite': favorite
        },
    )


class FavoriteRecipe(View, LoginRequiredMixin):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        result = JsonResponse({'success': False})
        request_body = json.loads(request.body)
        recipe_id = request_body.get('id')
        if recipe_id is not None:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            follow_obj, created = FollowRecipe.objects.get_or_create(
                recipe=recipe, user=request.user)
            if created:
                result = JsonResponse({'success': True})
        else:
            result = JsonResponse({'success': False}, 400)
        return result

    def delete(self, request, recipe_id):
        follow_obj = get_object_or_404(
            FollowRecipe, recipe=recipe_id, user=request.user)
        follow_obj.delete()
        return JsonResponse({'success': True})


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     recipe_id = self.kwargs.get('id')
    #     user = self.request.user
    #     follow_data = dict(user=user, recipe=recipe_id)
    #     follow_obj = get_object_or_None(FollowRecipe, **follow_data)
    #     # review = get_object_or_404(FollowRecipe, pk=review_id, title__pk=title_id)
    #     return follow_obj

    # def perform_create(self, serializer):
    #     recipe_id = self.kwargs.get('id')
    #     user = self.request.user
    #     follow_data = dict(user=user, recipe=recipe_id)
    #     follow_obj = get_object_or_None(FollowRecipe, **follow_data)
    #     serializer.save(**follow_data)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        pass


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'GET':
        all_tags = Tag.objects.all()
        recipe_tags = recipe.tag.all()
        ingredients = Ingridient.objects.all()
        recipe_ingredients = RecipeIngridient.objects.filter(
            recipe=recipe_id)
        if recipe.author == request.user:
            template = 'formChangeRecipe.html'
            return render(
                request, template,
                {
                    'recipe': recipe,
                    'all_tags': all_tags,
                    'recipe_tags': recipe_tags,
                    'ingredients': ingredients,
                    'recipe_ingredients': recipe_ingredients,
                },
            )
        else:
            return HttpResponseForbidden()
    elif request.method == 'POST':
        form = RecipeForm(user=request.user, data=request.POST)
        if form.is_valid():
            obj = form.save()
            return HttpResponse('ok')
        return HttpResponse('errors')

