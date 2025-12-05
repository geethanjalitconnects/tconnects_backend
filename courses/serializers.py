from rest_framework import serializers
from .models import (
    Course, Module, Lesson, Assignment, AssignmentQuestion,
    Enrollment, LessonProgress, AssignmentSubmission
)
from django.contrib.auth import get_user_model
User = get_user_model()

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "video_url", "duration", "is_preview", "order")


class AssignmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentQuestion
        fields = ("id", "question", "options")


class AssignmentSerializer(serializers.ModelSerializer):
    questions = AssignmentQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = ("id", "title", "questions")


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    assignment = AssignmentSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ("id", "title", "order", "lessons", "assignment")


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "title", "slug", "thumbnail", "price", "rating", "language")


class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "instructor",
            "description",
            "price",
            "rating",
            "language",
            "thumbnail",
            "level",
            "what_you_will_learn",   # ⭐ NEW
            "requirements",           # ⭐ NEW
            "course_includes",        # ⭐ NEW
            "modules",
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("id", "user", "course", "enrolled_at")
        read_only_fields = ("user", "enrolled_at")


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ("id", "user", "lesson", "completed", "completed_at")
        read_only_fields = ("user", "completed_at")


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ("id", "user", "assignment", "answers", "score", "submitted_at")
        read_only_fields = ("user", "score", "submitted_at")
