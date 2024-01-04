from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class BaseModelMixin(models.Model):
    created = models.DateTimeField(
        verbose_name="Создано",
        auto_now_add=True,
        auto_now=False,
    )
    modified = models.DateTimeField(
        verbose_name="Изменено",
        auto_now=True,
        auto_now_add=False,
    )

    class Meta:
        abstract = True


class Tag(BaseModelMixin):
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
        unique=True,
        null=False,
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=7,
        null=True,
    )
    slug = models.SlugField(
        verbose_name="слаг",
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name", "created")

    def __str__(self):
        return self.name


class MeasurementUnit(BaseModelMixin):
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"
        ordering = ("id",)

    def __str__(self):
        return self.measurement_unit


class Ingredient(BaseModelMixin):
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        verbose_name="Единица измерения",
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient",
            )
        ]

    def __str__(self):
        return self.name


class Recipe(BaseModelMixin):
    tags = models.ManyToManyField(
        Tag, verbose_name="Теги", through="RecipesTags"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        verbose_name="Ингридиенты",
        through="IngredientsRecipes",
    )
    favorites = models.ManyToManyField(
        User,
        related_name="favorites",
        through="Favorite",
    )
    shopping_cart = models.ManyToManyField(
        User,
        related_name="shopping_cart",
        through="ShoppingCart",
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="img/%Y/%m/%d",
    )
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created", "id")

    def __str__(self):
        return self.name


class RecipesTags(BaseModelMixin):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name="Тег",
    )

    class Meta:
        verbose_name = "Теги рецепта"
        verbose_name_plural = "Теги рецептов"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "tags"], name="unique_tags_for_recipe"
            )
        ]


class IngredientsRecipes(BaseModelMixin):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipes",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингридиент",
        related_name="ingredients",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество", null=False
    )

    class Meta:
        verbose_name = "Ингридиенты для рецепта"
        verbose_name_plural = "Ингридиенты для рецептов"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_ingredients_for_recipe",
            )
        ]


class FavoriteShopMixin(BaseModelMixin):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_%(class)s_for_user"
            )
        ]


class Favorite(FavoriteShopMixin):
    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ("id",)


class ShoppingCart(FavoriteShopMixin):
    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        ordering = ("id",)
