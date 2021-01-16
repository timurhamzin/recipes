from django.contrib import admin
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from recipe.models import RecipeIngridient, Recipe, Ingridient

User = get_user_model()


class RecipeIngridientInline(admin.StackedInline):
    model = RecipeIngridient


class MyUserAdmin(UserAdmin):
    list_filter = UserAdmin.list_filter + ('email', 'username',)


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('title',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'favorite_count', 'image_tag')
    list_filter = ('author', 'title', 'tag',)
    inlines = (RecipeIngridientInline,)
    exclude = ('ingridients',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# automatically register classes
class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_site)


def register_models():
    models = apps.get_models()
    for model in models:
        admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
        try:
            admin.site.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingridient, IngredientAdmin)
register_models()
