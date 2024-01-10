import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction

from helpfiles import constants
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers import UserSerializer

from .models import (
    Favorite,
    Ingredient,
    IngredientsRecipes,
    Recipe,
    ShoppingCart,
    Tag
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(
        source="measurement_unit.measurement_unit"
    )

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit.measurement_unit"
    )

    class Meta:
        model = IngredientsRecipes
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientsRecipesWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientsRecipes
        fields = ("id", "amount")

    def validate_amount(self, value):
        """Валидация поля количество"""
        if value < constants.MIN_INGREDIENT_AMOUNT:
            raise serializers.ValidationError("должно быть 1 или больше")
        return value


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeReadSerializer(
        many=True, read_only=True, source="recipes"
    )
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        return (
            self.context.get("request").user.is_authenticated
            and Favorite.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get("request").user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = IngredientsRecipesWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    def validate(self, attrs):
        """Валидация"""
        ingredients = attrs.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Должно быть не пустым"}
            )
        for ingredient in ingredients:
            if not Ingredient.objects.filter(id=ingredient["id"]).exists():
                raise ValidationError(
                    {"ingredients": "Указан ID несуществующего ингредиента"}
                )
        if not attrs.get("tags"):
            raise serializers.ValidationError(
                {"tags": "Должно быть не пустым"}
            )
        ingredients_id = [item["id"] for item in ingredients]
        unique_ingredients_id = set(ingredients_id)
        if len(unique_ingredients_id) != len(ingredients_id):
            raise ValidationError(
                {"ingredients": "Все значения должны быть уникальными"}
            )
        tags_id = [tag.id for tag in attrs.get("tags")]
        unique_tags_id = set(tags_id)
        if len(unique_tags_id) != len(tags_id):
            raise ValidationError(
                {"tags": "Все значения должны быть уникальными"}
            )
        return attrs

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        IngredientsRecipes.objects.bulk_create(
            [
                IngredientsRecipes(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(pk=ingredient["id"]),
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        IngredientsRecipes.objects.filter(
            recipe=instance, ingredient__in=instance.ingredients.all()
        ).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data
