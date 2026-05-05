from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


def set_auth_cookies(response, refresh):
    """Attach access and refresh JWTs as HTTP-only cookies on the response."""
    response.set_cookie("access_token", str(refresh.access_token), httponly=True, samesite="Lax")
    response.set_cookie("refresh_token", str(refresh), httponly=True, samesite="Lax")


def build_login_response(user):
    """Create a login response containing the user payload and auth cookies."""
    refresh = RefreshToken.for_user(user)
    response = Response({
        "detail": "Login successfully!",
        "user": {"id": user.id, "username": user.username, "email": user.email},
    }, status=status.HTTP_200_OK)
    set_auth_cookies(response, refresh)
    return response
