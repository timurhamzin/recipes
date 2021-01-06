from rest_framework.serializers import ModelSerializer

from recipe.models import Recipe


class RecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'user', 'recipe'
        )
        required_fields = fields

    def update(self, **kwargs):
        super().update(**kwargs)
        return Recipe.objects.create(**validated_data)
