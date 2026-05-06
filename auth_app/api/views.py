from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import CookieJWTAuthentication
from .serializers import LoginSerializer, RegistrationSerializer
from .utils import build_login_response


class RegisterView(APIView):
    """Handles user registration."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Create a new user account."""
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"detail": "User created successfully!"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Handles user login and issues JWT cookies."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Authenticate user and return access and refresh tokens as cookies."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return build_login_response(user)


class LogoutView(APIView):
    """Handles user logout by blacklisting the refresh token and clearing cookies."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist the refresh token and delete auth cookies."""
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except (TokenError, InvalidToken):
                pass

        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class TokenRefreshView(APIView):
    """Issues a new access token from a valid refresh token cookie."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Read the refresh token cookie and return a fresh access token cookie."""
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token missing."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except (TokenError, InvalidToken):
            return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({"detail": "Token refreshed"}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", access_token, httponly=True, samesite="Lax")
        return response



