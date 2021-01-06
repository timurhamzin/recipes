from rest_framework.serializers import ModelSerializer

from recipe.models import FollowRecipe


class FollowRecipeSerializer(ModelSerializer):
    class Meta:
        model = FollowRecipe
        fields = (
            'user', 'recipe'
        )
        required_fields = fields

    def create(self, validated_data):
        return FollowRecipe.objects.create(**validated_data)
