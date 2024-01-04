from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request

from .models import Recipe


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request: Request, view, obj: Recipe):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user