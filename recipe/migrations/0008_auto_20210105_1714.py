# Generated by Django 3.1.4 on 2021-01-05 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0007_tag_badge_color'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',)},
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='ingridients',
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingridients',
            field=models.ManyToManyField(related_name='recipes', through='recipe.RecipeIngridient', to='recipe.Ingridient'),
        ),
    ]
