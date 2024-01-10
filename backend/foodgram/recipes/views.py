from django.contrib.auth import get_user_model
from django.db import models
from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from users.pagination import FoodgramPaginator

from . import generate_pdf
from .filters import IngredientsSearchFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    RecipeWriteSerializer,
    TagSerializer
)

User = get_user_model()


class TagViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    search_fields = ["^name"]
    filter_backends = [IngredientsSearchFilter]


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = FoodgramPaginator
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = RecipeFilter
    http_method_names = ["get", "post", "patch", "create", "delete"]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            is_favorited = Favorite.objects.filter(
                recipe=models.OuterRef("pk"), user=self.request.user
            )
            is_in_shopping_cart = ShoppingCart.objects.filter(
                recipe=models.OuterRef("pk"), user=self.request.user
            )
        else:
            is_favorited = Favorite.objects.none()
            is_in_shopping_cart = ShoppingCart.objects.none()
        return (
            Recipe.objects.all()
            .select_related("author")
            .prefetch_related(
                "tags", "ingredients", "favorites", "shopping_cart"
            )
            .annotate(
                is_favorited=models.Exists(is_favorited),
                is_in_shopping_cart=models.Exists(is_in_shopping_cart),
            )
        )

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        return self.add_to(Favorite, request.user, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return self.add_to(ShoppingCart, request.user, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_from(ShoppingCart, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe = Recipe.objects.filter(id=pk).first()
        if recipe is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        recipe = Recipe.objects.filter(id=pk).first()
        obj = model.objects.filter(user=user, recipe__id=pk)
        if recipe is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        url_path="download_shopping_cart",
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        my_ingredients = (
            ShoppingCart.objects.filter(
                user=request.user,
            )
            .values("recipe__ingredients")
            .annotate(
                total_amount=models.Sum("recipe__recipes__amount"),
                ingredient=models.F("recipe__ingredients__name"),
                measurement_unit=models.F(
                    "recipe__ingredients__measurement_unit__measurement_unit"
                ),
            )
            .values_list(
                "ingredient",
                "total_amount",
                "measurement_unit",
            )
        )
        return generate_pdf_response(my_ingredients)


def generate_pdf_response(ingredients):
    pdfmetrics.registerFont(
        TTFont(
            generate_pdf.PDF_FONT_NAME,
            generate_pdf.PDF_FONT_DIR / generate_pdf.PDF_FONT_FILE,
        )
    )
    buffer = HttpResponse(content_type="application/pdf")
    buffer["Content-Disposition"] = 'attachment; filename="file.pdf"'
    canvas = Canvas(buffer)
    canvas.setFont(
        generate_pdf.PDF_FONT_NAME, generate_pdf.PDF_TITLE_FONT_SIZE
    )
    canvas.drawCentredString(
        A4[0] / 2, A4[1] - generate_pdf.PDF_INDENT, "Список покупок:"
    )
    canvas.setFont(generate_pdf.PDF_FONT_NAME, generate_pdf.PDF_TEXT_FONT_SIZE)
    for index, ingredient in enumerate(ingredients):
        canvas.drawString(
            generate_pdf.PDF_INDENT,
            A4[1]
            - generate_pdf.PDF_INDENT
            - (generate_pdf.PDF_TEXT_FONT_SIZE + generate_pdf.PDF_GAP)
            * (index + 1),
            (f"{ingredient[0]} {ingredient[1]} {ingredient[2]}"),
        )
    canvas.save()
    return buffer
