from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_app.models import Quiz, Question
from quiz_app.services.quiz_generator import generate_quiz_from_url
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
            quiz_data = generate_quiz_from_url(url)
        except Exception:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        quiz = self._save_quiz(request.user, quiz_data)
        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)