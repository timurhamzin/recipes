# Generated by Django 3.1.4 on 2021-01-05 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0008_auto_20210105_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cart',
            field=models.ManyToManyField(blank=True, to='recipe.ShoppingCart'),
        ),
    ]
