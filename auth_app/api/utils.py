from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken


def set_access_cookie(response, access_token):
    """Attach the access JWT as an HTTP-only cookie with matching max_age."""
    max_age = int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds())
    response.set_cookie("access_token", access_token, httponly=True, samesite="Lax", max_age=max_age)


def set_auth_cookies(response, refresh):
    """Attach access and refresh JWTs as HTTP-only cookies with matching max_age."""
    refresh_max_age = int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds())
    set_access_cookie(response, str(refresh.access_token))
    response.set_cookie("refresh_token", str(refresh), httponly=True, samesite="Lax", max_age=refresh_max_age)


def build_login_response(user):
    """Create a login response containing the user payload and auth cookies."""
    refresh = RefreshToken.for_user(user)
    response = Response({
        "detail": "Login successfully!",
        "user": {"id": user.id, "username": user.username, "email": user.email},
    }, status=status.HTTP_200_OK)
    set_auth_cookies(response, refresh)
    return response
