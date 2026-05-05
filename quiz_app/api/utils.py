from quiz_app.models import Quiz, Question


def save_quiz(owner, quiz_data):
    """Persist a quiz and its questions for the given owner."""
    questions_data = quiz_data.pop('questions', [])
    quiz = Quiz.objects.create(owner=owner, **quiz_data)
    for question in questions_data:
        Question.objects.create(quiz=quiz, **question)
    return quiz
