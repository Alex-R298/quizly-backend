from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Only the profile owner may modify the profile."""

    def has_object_permission(self, request, view, obj):
        """Allow read access to all; restrict write access to the object owner."""
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.user == request.user