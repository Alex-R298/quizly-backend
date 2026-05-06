from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Only the owner of a quiz may access or modify it."""

    def has_object_permission(self, request, view, obj):
        """Allow access only if the requesting user owns the quiz."""
        return obj.owner == request.user
