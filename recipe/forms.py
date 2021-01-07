from django.forms import ModelForm

from recipe.models import Recipe


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'
