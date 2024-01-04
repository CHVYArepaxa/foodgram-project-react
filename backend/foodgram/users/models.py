from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.settings import USERNAME_CHARSET


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


class User(AbstractUser, BaseModelMixin):
    email = models.EmailField(
        verbose_name="Почта",
        null=False,
        unique=True,
        max_length=254,
    )
    username = models.CharField(
        verbose_name="Имя пользователя",
        unique=True,
        null=False,
        max_length=150,
        validators=[
            RegexValidator(
                USERNAME_CHARSET,
                message="Имя пользователя содержит недопустимый символ",
            ),
        ],
    )
    first_name = models.CharField(
        verbose_name="Имя",
        null=False,
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        null=False,
        max_length=150,
    )
    subscriptions = models.ManyToManyField(
        "User",
        related_name="users",
        verbose_name="Подписки",
        through="Sub",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("id",)
        constraints = (
            models.UniqueConstraint(
                fields=("username",), name="unique_username"
            ),
            models.UniqueConstraint(fields=("email",), name="unique_email"),
        )

    def __str__(self):
        return self.username


class Sub(BaseModelMixin):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, related_name="subs"
    )
    subscription = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, related_name="users_subs"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("id",)
