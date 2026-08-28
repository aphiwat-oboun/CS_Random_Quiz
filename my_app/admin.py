from django.contrib import admin
from .models import Category, Question, QuizLog
from .firebase_config import sync_question_to_firestore, delete_question_from_firestore


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "created_at")
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "category", "difficulty", "correct_choice", "is_active", "created_at")
    list_filter = ("category", "difficulty", "is_active")
    search_fields = ("text", "choice_a", "choice_b", "choice_c", "choice_d")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        sync_question_to_firestore(obj)

    def delete_model(self, request, obj):
        delete_question_from_firestore(obj.id)
        super().delete_model(request, obj)


@admin.register(QuizLog)
class QuizLogAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "played_at", "is_correct")
    list_filter = ("played_at", "is_correct")
