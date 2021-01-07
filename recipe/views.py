import json
from typing import Type
from urllib.response import addbase

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Model, Q
from django.forms import modelform_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden, QueryDict
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from recipe.forms import RecipeForm
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
    recipes = Recipe.objects.filter(
        Q(tag__name__in=selected_tags) | Q(tag=None)).distinct()

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


def get_recipe_data(request):
    raw_data = request.POST.dict()
    result = {'image': raw_data['file'], 'description': raw_data['discription'],
              'title': raw_data['name'],
              'cooking_time': raw_data['cooking_time']}
    return result


def create_recipe_tags(recipe, request):
    raw_data = request.POST.dict()
    all_tags = Tag.objects.all()
    tags_to_set = [k for k in raw_data.keys() if k in all_tags]
    present_tags = recipe.tag.all()
    present_tags_set = set(present_tags)
    tags_to_set_set = set(tags_to_set)
    if present_tags_set != tags_to_set_set:
        remove_tags = present_tags_set - tags_to_set_set
        add_tags = tags_to_set_set - present_tags_set
        recipe.tag.remove(*remove_tags)
        recipe.tag.add(*add_tags)
    recipe.save()


def create_recipe_ingredients(recipe, request):
    raw_data = request.POST.dict()
    RecipeIngridient.objects.filter(recipe__id=recipe.id).delete()
    ingredient_titles = [raw_data[k] for k in raw_data.keys()
                        if k.startswith('nameIngredient')]
    amounts = [raw_data[k] for k in raw_data.keys()
               if k.startswith('valueIngredient')]
    for ingredient_title, amount in zip(ingredient_titles, amounts):
        ingredient = get_object_or_404(Ingridient, title=ingredient_title)
        RecipeIngridient.objects.create(recipe=recipe, ingridient=ingredient,
                                        amount=amount)


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'GET':
        all_tags = Tag.objects.all()
        recipe_tags = recipe.tag.all()
        ingredients = Ingridient.objects.all()
        recipe_ingredients = RecipeIngridient.objects.filter(
            recipe=recipe_id)
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
    elif request.method == 'POST':
        data = get_recipe_data(request)
        Form = modelform_factory(
            Recipe, form=RecipeForm, fields=(data.keys())
        )
        form = Form(data, instance=recipe)
        if form.is_valid():
            form.save()
            create_recipe_tags(recipe, request)
            create_recipe_ingredients(recipe, request)
            return JsonResponse({'success': True})
        else:
            print(form.errors)
        return JsonResponse({'success': False}, 422)


# TODO
# remove url for this view, it's for testing purposes only
@login_required
def edit_model_form(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            obj = form.save(
                commit=False)  # does nothing, just trigger the validation
            print(obj)
            for ingredient in obj.ingridients.all():
                ingredient.amount = 1
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipeEditModelForm.html', {'form': form})
