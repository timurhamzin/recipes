from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

from recipe.models import RecipeIngridient, Recipe


class RecipeIngridientInline(admin.StackedInline):
    model = RecipeIngridient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'favorite_count')
    list_filter = ('author', 'title', 'tag',)
    inlines = (RecipeIngridientInline,)
    # fieldsets = (
    #     (None, {
    #         'fields': ('author', 'title', 'image', 'description',
    #                    'tags', 'cooking_time')
    #     }),
    #     ('Advanced options', {
    #         'classes': ('collapse',),
    #         'fields': [],
    #     }),
    # )


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


register_models()
try:
    admin.site.register(Recipe, RecipeAdmin)
except AlreadyRegistered:
    admin.site.unregister(Recipe)
    admin.site.register(Recipe, RecipeAdmin)
