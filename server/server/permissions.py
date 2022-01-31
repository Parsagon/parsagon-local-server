from rest_framework import permissions
from django.conf import settings


class HasAuthToken(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.META.get('HTTP_X_APIKEY') == settings.API_KEY
