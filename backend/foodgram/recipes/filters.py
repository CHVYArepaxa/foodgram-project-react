from django_filters import FilterSet, filters
from rest_framework.filters import SearchFilter

from .models import Recipe, Tag


class IngredientsSearchFilter(SearchFilter):
    search_param = "name"


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(method="is_favorited_filter")
    is_in_shopping_cart = filters.NumberFilter(
        method="is_in_shopping_cart_filter"
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
        )

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcart__user=user)
        return queryset
