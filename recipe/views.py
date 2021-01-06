import json
from typing import Type

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Model
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from recipe.models import Recipe, Tag, RecipeIngridient, FollowRecipe
from recipe.serializers import FollowRecipeSerializer

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


@login_required
@csrf_exempt
def favorites(request):
    result = {'success': False}
    if request.method == 'POST':
        if request.body:
            print('INSIDE')
            print('INSIDE')
            print('INSIDE')
            body = json.loads(request.body)
            recipe_id = body.get('id')
            follow_obj = None
            follow_data = dict(user=request.user.id, recipe=recipe_id)
            if recipe_id is not None:
                follow_obj = get_object_or_None(FollowRecipe, **follow_data)
            if follow_obj is None:
                serializer = FollowRecipeSerializer(data=follow_data)
                if serializer.is_valid():
                    serializer.save()
                    result = follow_data
            else:
                follow_obj.delete()
                result = {'success': True}
                print('RESULT')
                print('RESULT')
                print('RESULT')
                print(result)
    return JsonResponse(result)


# class FollowRecipeViewSet(viewsets.ModelViewSet):
#     serializer_class = FollowRecipeSerializer
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
#     def perform_create(self, serializer):
#         recipe_id = self.kwargs.get('id')
#         user = self.request.user
#         follow_data = dict(user=user, recipe=recipe_id)
#         follow_obj = get_object_or_None(FollowRecipe, **follow_data)
#         serializer.save(**follow_data)
#
#
#
#
# class UserViewSet(viewsets.ModelViewSet):
#     """
#     A viewset for viewing and editing user instances.
#     """
#     serializer_class = UserSerializer
#     queryset = User.objects.all()