from __future__ import annotations
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_author')
    title = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipe_images/',
        blank=True,
        null=True)
    description = models.TextField()
    ingridients = models.ManyToManyField('Ingridient')
    tag = models.ManyToManyField('Tag')
    cooking_time = models.IntegerField()
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    cart = models.ManyToManyField('ShoppingCart',  related_name='recipes',
                                  blank=True)
    favorite_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


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

    def __str__(self):
        return f'User {self.user} follows author {self.author}'


class ShoppingCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
