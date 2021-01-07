from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.safestring import mark_safe

User = get_user_model()


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    image_upload_to = 'recipe_images'
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author')
    title = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to=image_upload_to,
        blank=True,
        null=True)
    description = models.TextField()
    ingridients = models.ManyToManyField('Ingridient',
                                         through='RecipeIngridient', related_name='recipes')
    tag = models.ManyToManyField('Tag', blank=False)
    cooking_time = models.IntegerField()
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    cart = models.ManyToManyField('ShoppingCart',
                                  blank=True)
    favorite_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe(f'<img src="{settings.MEDIA_URL}'
                         f'{self.image}" height="30"/>')

    image_tag.short_description = 'Image'

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    class Meta:
        ordering = ('-pub_date',)


class Ingridient(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(max_length=20,
                                        verbose_name='Единица измерения')
    part = models.ManyToManyField(Recipe, through='RecipeIngridient')

    def __str__(self):
        return self.title


class RecipeIngridient(models.Model):
    ingridient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
        related_name='ingridients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    amount = models.PositiveSmallIntegerField()


class Tag(models.Model):
    name = models.CharField(max_length=10)
    badge_colors = (
        ('orange', 'orange'),
        ('green', 'green'),
        ('purple', 'purple'),
    )
    badge_color = models.CharField(
        max_length=32,
        choices=badge_colors,
        default='orange',
    )

    def __str__(self):
        return self.name


class FollowRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_follower')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='followed_recipe')

    class Meta:
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f'User {self.user} follows recipe {self.recipe}'


class FollowUser(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed')

    class Meta:
        unique_together = ['user', 'author']

    def __str__(self):
        return f'User {self.user} follows author {self.author}'


class ShoppingCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
