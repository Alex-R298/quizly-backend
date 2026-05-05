import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)

from quiz_app.models import Quiz, Question
from quiz_app.services.quiz_generator import generate_quiz_from_url
from quiz_app.services.youtube import normalize_url
from .serializers import QuizSerializer
from .permissions import IsOwner
from auth_app.api.authentication import CookieJWTAuthentication


class QuizViewSet(viewsets.ModelViewSet):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = QuizSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Quiz.objects.filter(owner=self.request.user)

    def get_object(self):
        pk = self.kwargs['pk']
        if not str(pk).lstrip('-').isdigit():
            raise ValidationError({"detail": f"Invalid quiz ID: '{pk}'."})
        obj = get_object_or_404(Quiz, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def _save_quiz(self, owner, quiz_data):
        questions_data = quiz_data.pop('questions', [])
        quiz = Quiz.objects.create(owner=owner, **quiz_data)
        for question in questions_data:
            Question.objects.create(quiz=quiz, **question)
        return quiz

    def create(self, request, *args, **kwargs):
        url = request.data.get('url')
        if not url:
            return Response({"detail": "URL is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            normalized_url = normalize_url(url)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quiz_data = generate_quiz_from_url(normalized_url)
        except Exception:
            logger.exception("Quiz generation failed")
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        quiz = self._save_quiz(request.user, quiz_data)
        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)