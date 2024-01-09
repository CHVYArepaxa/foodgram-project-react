from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from helpfiles import constants
from helpfiles.Basemodel import BaseModelMixin

from foodgram.settings import USERNAME_CHARSET


class User(AbstractUser, BaseModelMixin):
    email = models.EmailField(
        verbose_name="Почта",
        null=False,
        unique=True,
        max_length=constants.EMAIL_MAX_LEN,
    )
    username = models.CharField(
        verbose_name="Имя пользователя",
        unique=True,
        null=False,
        max_length=constants.USERNAME_MAX_LEM,
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
        max_length=constants.FIRST_NAME_MAX_LEN,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        null=False,
        max_length=constants.LAST_NAME_MAX_LEN,
    )
    subscriptions = models.ManyToManyField(
        "User",
        related_name="users",
        verbose_name="Подписки",
        through="Sub",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

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
