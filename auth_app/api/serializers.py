from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates and creates a new user account."""

    email = serializers.EmailField(required=True)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmed_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        """Check password confirmation and email uniqueness."""
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError({'confirmed_password': 'Passwords do not match.'})
        validate_password(attrs['password'])
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        return attrs

    def create(self, validated_data):
        """Persist the new user to the database."""
        validated_data.pop('confirmed_password')
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
