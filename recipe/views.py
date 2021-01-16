import json
from typing import Type

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Model, Q, Prefetch
from django.forms import modelform_factory, ModelForm
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.core.files.storage import default_storage

from recipe.forms import RecipeForm
from recipe.models import Recipe, Tag, RecipeIngridient, FollowRecipe, \
    Ingridient, ShoppingCart, FollowUser
from recipe.templatetags.user_title import user_title
from recipe.views_helpers.helpers import serve_shopping_list

User = get_user_model()

CARDS_PER_PAGE = 6
FOLLOWED_PER_PAGE = 6
DEFAULT_TAG_VALUE = 1


def get_object_or_None(model: Type[Model], **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def index(request, only_favorite=False, by_author=None):
    # set context variables
    user = request.user
    get_dict = request.GET.dict()
    all_tags = Tag.objects.all()
    selected_tags = [t.name for t in all_tags
                     if get_dict.get(t.name, str(DEFAULT_TAG_VALUE)) == '1']

    # select recipes
    recipes = Recipe.objects.filter(
        Q(tag__name__in=selected_tags) | Q(tag=None))
    title = 'Рецепты'
    if request.user.is_authenticated:
        followed = list(user.follow_recipes.values_list('recipe', flat=True))
        purchased_recipes = list(
            user.purchased_recipes.values_list('id', flat=True))
        if only_favorite:
            title = f'Избранные рецепты'
            recipes = recipes.filter(id__in=followed)
    else:
        followed = None
        purchased_recipes = None

    if by_author is not None:
        selected_author = get_object_or_404(User, id=by_author)
        title = user_title(selected_author)
        recipes = recipes.filter(author=by_author)

    recipes = recipes.order_by('-pub_date').distinct()

    # set pages
    paginator = Paginator(recipes, CARDS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    return render(
        request, 'indexAuth.html',
        {
            'page': page,
            'paginator': paginator,
            'recipes': recipes,
            'all_tags': all_tags,
            'tag_filters': {},
            'shopping_cart': {},
            'purchased': purchased_recipes,
            'favorites': followed,
            'page_title': title,
            'by_author': by_author,
        },
    )


def favorite_list(request):
    return index(request, only_favorite=True)


@login_required
def my_followed(request):
    user = request.user
    author_ids = list(user.follows.values_list('author', flat=True))
    authors = User.objects.filter(id__in=author_ids).all()
    paginator = Paginator(authors, FOLLOWED_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    return render(
        request, 'myFollow.html',
        {
            'page': page,
            'paginator': paginator,
            'authors': authors
        },
    )


@login_required
def shopping_cart(request):
    user = request.user
    download = request.GET.get('download')
    if download:
        return serve_shopping_list(request)
    else:
        recipe_ids = list(user.purchased.values_list('recipe', flat=True))
        recipes = Recipe.objects.filter(id__in=recipe_ids).all()
        return render(
            request, 'shopList.html',
            {
                'recipes': recipes
            },
        )


def author(request, author_id):
    return index(request, by_author=author_id)


def single_page(request, recipe_id):
    recipe = get_object_or_404(Recipe.objects.prefetch_related(
        Prefetch('recipeingridient_set', to_attr='recipe_ingredients')),
        id=recipe_id)
    return render(
        request, 'singlePage.html',
        {
            'recipe': recipe,
            'tags': recipe.tag.all(),
            'recipe_ingredients': recipe.recipe_ingredients,
            'favorite': FollowRecipeView.is_followed(recipe, request.user),
            'in_cart': ShoppingCartView.is_followed(recipe, request.user),
            'subscribed': FollowUserView.is_followed(
                recipe.author, request.user)
        },
    )


class FollowThrough(View, LoginRequiredMixin):
    # override class attributes in child classes
    _followed_through_name = ''
    _followed_class = None
    _through_class = None
    _follow_counter_field_name = ''

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        result = JsonResponse({'success': False})
        request_body = json.loads(request.body)
        followed_id = request_body.get('id')
        if followed_id is not None:
            followed_obj = get_object_or_404(
                self._followed_class, id=followed_id)
            filter_kwargs = {self._followed_through_name: followed_obj}
            through_obj, created = self._through_class.objects.get_or_create(
                user=request.user, **filter_kwargs)
            if created:
                result = JsonResponse({'success': True})
            self.update_counter(followed_obj, 1)
        else:
            result = JsonResponse({'success': False}, 400)
        return result

    def delete(self, request, followed_id):
        filter_kwargs = {self._followed_through_name: followed_id}
        try:
            through_obj = get_object_or_404(
                self._through_class.objects.select_related(
                    self._followed_through_name),
                user=request.user, **filter_kwargs
            )
            followed_obj = getattr(through_obj, self._followed_through_name)
            through_obj.delete()
            self.update_counter(followed_obj, -1)
        except Http404:
            pass
        return JsonResponse({'success': True})

    @classmethod
    def is_followed(cls, followed, user):
        if user.is_authenticated:
            filter_kwargs = {cls._followed_through_name: followed}
            found = get_object_or_None(cls._through_class,
                                       user=user, **filter_kwargs)
        else:
            return False
        return found is not None

    def update_counter(self, followed_obj, add):
        if self._follow_counter_field_name:
            count = getattr(followed_obj, self._follow_counter_field_name)
            setattr(followed_obj, self._follow_counter_field_name, count + add)
            followed_obj.save()


class FollowRecipeView(FollowThrough):
    _followed_through_name = 'recipe'
    _followed_class = Recipe
    _through_class = FollowRecipe
    _follow_counter_field_name = 'favorite_count'


class FollowUserView(FollowThrough):
    _followed_through_name = 'author'
    _followed_class = User
    _through_class = FollowUser


class ShoppingCartView(FollowThrough):
    _followed_through_name = 'recipe'
    _followed_class = Recipe
    _through_class = ShoppingCart


@login_required
def edit_recipe(request, recipe_id):
    if recipe_id is not None:
        recipe = get_object_or_404(Recipe, id=recipe_id)
    else:
        recipe = Recipe(author=request.user)
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
        return redirect(
            reverse('single_page', kwargs=dict(recipe_id=recipe.id)))


@login_required
def create_recipe(request):
    return edit_recipe(request, None)


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

    def get_tags(self):
        if self._recipe.id is not None:
            return self._recipe.tag.all()
        else:
            return []

    def render_get(self):
        all_tags = Tag.objects.all()
        ingredients = Ingridient.objects.all()
        recipe_tags = self.get_tags()
        if self._recipe.id is not None:
            recipe_ingredients = RecipeIngridient.objects.filter(
                recipe=self._recipe.id)
            form_title = 'Редактирование рецепта'
            save_title = 'Сохранить'
            edit_mode = True
        else:
            recipe_ingredients = []
            form_title = 'Создание рецепта'
            save_title = 'Создать рецепт'
            edit_mode = False
        template = 'formCreateOrEditRecipe.html'
        return render(
            self._request, template,
            {
                'recipe': self._recipe,
                'all_tags': all_tags,
                'recipe_tags': recipe_tags,
                'ingredients': ingredients,
                'recipe_ingredients': recipe_ingredients,
                'form_title': form_title,
                'save_title': save_title,
                'edit_mode': edit_mode,
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
# remove this view, it's for testing purposes only
# @login_required
# def edit_model_form(request, recipe_id):
#     recipe = get_object_or_404(Recipe, id=recipe_id)
#     if request.method == 'POST':
#         form = RecipeForm(request.POST, instance=recipe)
#         if form.is_valid():
#             obj = form.save(
#                 commit=False)  # does nothing, just trigger the validation
#             for ingredient in obj.ingridients.all():
#                 ingredient.amount = 1
#     else:
#         form = RecipeForm(instance=recipe)
#     return render(request, 'recipeEditModelForm.html', {'form': form})
