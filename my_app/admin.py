from django.contrib import admin
from .models import Category, Question, QuizLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "created_at")
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "category", "difficulty", "correct_choice", "is_active", "created_at")
    list_filter = ("category", "difficulty", "is_active")
    search_fields = ("text", "choice_a", "choice_b", "choice_c", "choice_d")


@admin.register(QuizLog)
class QuizLogAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "played_at", "is_correct")
    list_filter = ("played_at", "is_correct")
