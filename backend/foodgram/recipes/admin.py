from django.contrib import admin

from .models import (
    Ingredient,
    IngredientsRecipes,
    MeasurementUnit,
    Recipe,
    RecipesTags,
    Tag
)


class TagAdmin(admin.ModelAdmin):
    list_filter = ("name",)
    search_fields = ("name",)
    list_display = ("name", "slug")
    list_display_links = ("name", "slug")


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("name",)
    search_fields = ("name",)


class RecipesTagsInline(admin.TabularInline):
    model = RecipesTags
    extra = 0


class IngredientsRecipesInline(admin.TabularInline):
    model = IngredientsRecipes
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ("name", "author", "tags")
    search_fields = ("name", "text")
    list_display = (
        "name",
        "author",
    )
    list_display_links = ("name",)
    inlines = (IngredientsRecipesInline, RecipesTagsInline)


admin.site.register(MeasurementUnit)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
