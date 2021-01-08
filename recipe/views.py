import json
from typing import Type
from urllib.response import addbase

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Model, Q
from django.forms import modelform_factory, ModelForm
from django.http import HttpResponseRedirect, HttpResponseForbidden, QueryDict
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from recipe.forms import RecipeForm
from recipe.models import Recipe, Tag, RecipeIngridient, FollowRecipe, \
    Ingridient, ShoppingCart
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
    if user.is_authenticated:
        template = 'singlePage.html'
    else:
        template = 'singlePageNotAuth.html'

    recipe_ingredients = RecipeIngridient.objects.filter(
        recipe=recipe_id)
    return render(
        request, template,
        {
            'recipe': recipe,
            'tags': recipe.tag.all(),
            'recipe_ingredients': recipe_ingredients,
            'favorite': FavoriteRecipe.is_favorite(recipe, request.user),
            'in_cart': Purchase.is_purchased(recipe, request.user)
        },
    )


class FavoriteRecipe(View, LoginRequiredMixin):

    #TODO
    # Add csrf support
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

    @staticmethod
    def is_favorite(recipe, user):
        found = get_object_or_None(FollowRecipe, user=user.id, recipe=recipe)
        return found is not None


# TODO
# refactor into one class with FavoriteRecipe
class Purchase(View, LoginRequiredMixin):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        result = JsonResponse({'success': False})
        request_body = json.loads(request.body)
        recipe_id = request_body.get('id')
        if recipe_id is not None:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            cart_obj, created = ShoppingCart.objects.get_or_create(
                recipe=recipe, user=request.user)
            if created:
                result = JsonResponse({'success': True})
        else:
            result = JsonResponse({'success': False}, 400)
        return result

    def delete(self, request, recipe_id):
        cart_obj = get_object_or_None(ShoppingCart, recipe__id=recipe_id,
                                      user=request.user)
        if cart_obj is not None:
            cart_obj.delete()
        return JsonResponse({'success': True})

    @staticmethod
    def is_purchased(recipe, user):
        item = get_object_or_None(ShoppingCart, user=user, recipe=recipe)
        return item is not None


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    editor = RecipeEditor(recipe, request)
    if recipe.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'GET':
        return editor.render_get()
    elif request.method == 'POST':
        form = editor.validate_recipe_with_form()
        if form:
            form.save()
            editor.update_recipe_image()
            editor.create_recipe_tags()
            editor.create_recipe_ingredients()
        return redirect(request.path_info)


@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return HttpResponseForbidden()
    recipe.delete()
    return redirect('/')


class RecipeEditor(object):

    def __init__(self, recipe, request):
        self._recipe = recipe
        self._request = request

    def render_get(self):
        all_tags = Tag.objects.all()
        recipe_tags = self._recipe.tag.all()
        ingredients = Ingridient.objects.all()
        recipe_ingredients = RecipeIngridient.objects.filter(
            recipe=self._recipe.id)
        template = 'formChangeRecipe.html'
        return render(
            self._request, template,
            {
                'recipe': self._recipe,
                'all_tags': all_tags,
                'recipe_tags': recipe_tags,
                'ingredients': ingredients,
                'recipe_ingredients': recipe_ingredients,
            },
        )

    def update_recipe_image(self):
        if 'file' in self._request.FILES.keys():
            image = self._request.FILES['file']
            self._recipe.image.save(
                default_storage.get_available_name(image.name), image)

    def validate_recipe_with_form(self) -> ModelForm:
        data = self.get_recipe_data()
        Form = modelform_factory(Recipe, form=RecipeForm, fields=data.keys())
        form = Form(data, instance=self._recipe)
        if form.is_valid():
            return form

    def get_recipe_data(self):
        raw_data = self._request.POST.dict()
        result = {'description': raw_data['discription'],
                  'title': raw_data['name'],
                  'cooking_time': raw_data['cooking_time']}
        return result

    def create_recipe_tags(self):
        raw_data = self._request.POST.dict()
        all_tags = Tag.objects.all()
        tags_to_set = [k for k in raw_data.keys()
                       if k in list(all_tags.values_list('name', flat=True))]
        present_tags = self._recipe.tag.all()
        present_tags_set = set(present_tags.values_list('name', flat=True))
        tags_to_set_set = set(tags_to_set)
        if present_tags_set != tags_to_set_set:
            remove_tags = present_tags_set - tags_to_set_set
            add_tags = tags_to_set_set - present_tags_set
            if remove_tags:
                self._recipe.tag.remove(*list(
                    all_tags.filter(
                        name__in=remove_tags).values_list('id', flat=True)))
            if add_tags:
                self._recipe.tag.add(
                    *all_tags.filter(
                        name__in=add_tags).values_list('id', flat=True))
        self._recipe.save()

    def create_recipe_ingredients(self):
        raw_data = self._request.POST.dict()
        RecipeIngridient.objects.filter(recipe__id=self._recipe.id).delete()
        ingredient_titles = [raw_data[k] for k in raw_data.keys()
                             if k.startswith('nameIngredient')]
        amounts = [raw_data[k] for k in raw_data.keys()
                   if k.startswith('valueIngredient')]
        for ingredient_title, amount in zip(ingredient_titles, amounts):
            ingredient = get_object_or_404(Ingridient, title=ingredient_title)
            RecipeIngridient.objects.create(recipe=self._recipe,
                                            ingridient=ingredient,
                                            amount=amount)


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

# class RecipeViewSet(viewsets.ModelViewSet):
#     serializer_class = RecipeSerializer
#     permission_classes = [IsAuthenticated]
#
#     # def get_queryset(self):
#     #     recipe_id = self.kwargs.get('id')
#     #     user = self.request.user
#     #     follow_data = dict(user=user, recipe=recipe_id)
#     #     follow_obj = get_object_or_None(FollowRecipe, **follow_data)
#     #     # review = get_object_or_404(FollowRecipe, pk=review_id, title__pk=title_id)
#     #     return follow_obj
#
#     # def perform_create(self, serializer):
#     #     recipe_id = self.kwargs.get('id')
#     #     user = self.request.user
#     #     follow_data = dict(user=user, recipe=recipe_id)
#     #     follow_obj = get_object_or_None(FollowRecipe, **follow_data)
#     #     serializer.save(**follow_data)
#
#     def perform_update(self, serializer):
#         super().perform_update(serializer)
#         pass
#
#
