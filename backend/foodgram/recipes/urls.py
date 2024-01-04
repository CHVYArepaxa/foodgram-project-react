from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register("recipes", RecipeViewSet, basename="Recipes")
router.register("ingredients", IngredientViewSet, basename="Ingredients")
router.register("tags", TagViewSet, basename="Tags")

urlpatterns = [path("", include(router.urls))]
