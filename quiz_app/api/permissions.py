from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Only the owner of a quiz may access or modify it."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
