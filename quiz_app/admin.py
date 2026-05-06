from django.contrib import admin

from quiz_app.models import Quiz, Question


class QuestionInline(admin.TabularInline):
    """Inline editor for questions within the quiz admin view."""

    model = Question
    extra = 0
    fields = ['question_title', 'question_options', 'answer']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin configuration for Quiz, including inline question editing."""

    list_display = ['title', 'owner', 'created_at', 'updated_at']
    search_fields = ['title', 'owner__username']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for individual questions."""

    list_display = ['question_title', 'quiz', 'answer']
    search_fields = ['question_title', 'quiz__title']
