from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator

User = get_user_model()
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import JSONField  # Only if using Postgres


class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True)
    instructor = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    price = models.CharField(max_length=64, default="FREE")
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    language = models.CharField(max_length=64, default="English")

    thumbnail = models.URLField(blank=True)
    level = models.CharField(max_length=64, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ⭐⭐⭐ NEW IMPORTANT FIELDS ⭐⭐⭐
    
    # "What you'll learn" – list of bullet points
    what_you_will_learn = models.JSONField(default=list, blank=True)

    # Requirements – list of prerequisites
    requirements = models.JSONField(default=list, blank=True)

    # Course includes – dictionary of structured data
    # Example: {"videos": 15, "modules": 5, "resources": 8, "access": "Lifetime"}
    course_includes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:255]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.pk})"



class Module(models.Model):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course.title} — Module {self.order}: {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_url = models.URLField(blank=True)  # Option C: store URL only
    duration = models.CharField(max_length=64, blank=True)
    is_preview = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("module", "order")

    def __str__(self):
        return f"{self.module.course.title} — {self.title}"


class Assignment(models.Model):
    module = models.OneToOneField(Module, related_name="assignment", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.module.course.title} — {self.title}"


class AssignmentQuestion(models.Model):
    assignment = models.ForeignKey(Assignment, related_name="questions", on_delete=models.CASCADE)
    question = models.TextField()
    # options saved as JSON array of strings
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Q#{self.pk} — {self.assignment.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name="enrollments", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")


class LessonProgress(models.Model):
    user = models.ForeignKey(User, related_name="lesson_progress", on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name="progress", on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "lesson")


class AssignmentSubmission(models.Model):
    user = models.ForeignKey(User, related_name="assignment_submissions", on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, related_name="submissions", on_delete=models.CASCADE)
    answers = models.JSONField(default=dict)  # {question_id: chosen_option}
    score = models.FloatField(default=0.0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "assignment")
