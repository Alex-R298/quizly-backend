from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from quiz_app.models import Quiz, Question


class GenerateQuizTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    @patch("quiz_app.api.views.generate_quiz_from_url")
    def test_create_quiz_success(self, mock_generate):
        mock_generate.return_value = {
            "title": "Quiz Title",
            "description": "Quiz Description",
            "questions": [
                {
                    "question_title": "Question 1",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "A",
                }
            ],
        }
        response = self.client.post('/api/quizzes/', {"url": self.valid_url}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
  

    @patch("quiz_app.api.views.generate_quiz_from_url")
    def test_create_quiz_invalid_url(self, mock_generate):
        response = self.client.post('/api/quizzes/', {"url": "not-a-url"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_generate.assert_not_called()

    @patch("quiz_app.api.views.generate_quiz_from_url")
    def test_create_quiz_missing_url(self, mock_generate):
        response = self.client.post('/api/quizzes/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_generate.assert_not_called()

    def test_create_quiz_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/quizzes/', {"url": self.valid_url}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("quiz_app.api.views.generate_quiz_from_url")
    def test_create_quiz_internal_error(self, mock_generate):
        mock_generate.side_effect = Exception("yt-dlp failed")
        response = self.client.post('/api/quizzes/', {"url": self.valid_url}, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizModelTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(
            owner=self.user,
            title="Test Quiz",
            description="Test",
            video_url="https://www.youtube.com/watch?v=example",
        )
        
    def test_quiz_creation(self):
        self.assertEqual(self.quiz.owner, self.user)
        self.assertEqual(self.quiz.title, "Test Quiz")
        self.assertEqual(self.quiz.description, "Test")
        self.assertEqual(self.quiz.video_url, "https://www.youtube.com/watch?v=example")

    def test_question_creation(self):
        question = Question.objects.create(
            quiz=self.quiz,
            question_title="What is 2+2?",
            question_options=["1", "2", "3", "4"],
            answer="4",
        )
        self.assertEqual(question.quiz, self.quiz)
        self.assertEqual(question.question_title, "What is 2+2?")
        self.assertEqual(question.question_options, ["1", "2", "3", "4"])
        self.assertEqual(question.answer, "4")


class GetQuizListTestCase(APITestCase): 
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        Quiz.objects.create(
            owner=self.user,
            title="Quiz 1",
            description="Description 1",
            video_url="https://www.youtube.com/watch?v=example1",
        )
        Quiz.objects.create(
            owner=self.user,
            title="Quiz 2",
            description="Description 2",
            video_url="https://www.youtube.com/watch?v=example2",
        )

    def test_get_quiz_list_success(self):
        response = self.client.get('/api/quizzes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], "Quiz 1")
        self.assertEqual(response.data[1]['title'], "Quiz 2")

    def test_get_quiz_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/quizzes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class GetQuizDetailTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(
            owner=self.user,
            title="Test Quiz",
            description="Test",
            video_url="https://www.youtube.com/watch?v=example",
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_title="What is 2+2?",
            question_options=["1", "2", "3", "4"],
            answer="4",
        )

    def test_get_quiz_detail_success(self):
        response = self.client.get(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Quiz")
        self.assertEqual(response.data['description'], "Test")
        self.assertEqual(response.data['video_url'], "https://www.youtube.com/watch?v=example")
        self.assertEqual(len(response.data['questions']), 1)
        question_data = response.data['questions'][0]
        self.assertEqual(question_data['question_title'], "What is 2+2?")
        self.assertEqual(question_data['question_options'], ["1", "2", "3", "4"])
        self.assertEqual(question_data['answer'], "4")

    def test_get_quiz_detail_not_found(self):
        response = self.client.get('/api/quizzes/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_quiz_detail_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f'/api/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class PatchQuizTestCase(APITestCase): 
    pass


class DeleteQuizTestCase(APITestCase):
    pass