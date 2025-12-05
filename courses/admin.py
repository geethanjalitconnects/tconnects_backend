from django.contrib import admin
from .models import Course, Module, Lesson, Assignment, AssignmentQuestion, Enrollment, LessonProgress, AssignmentSubmission

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0

class ModuleAdmin(admin.ModelAdmin):
    list_display = ("course", "order", "title")
    inlines = [LessonInline]

class AssignmentQuestionInline(admin.TabularInline):
    model = AssignmentQuestion
    extra = 0

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("module", "title")
    inlines = [AssignmentQuestionInline]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "rating")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Basic Info", {"fields": ("title", "slug", "instructor", "rating", "language")}),
        ("Course Content", {"fields": ("what_you_will_learn", "requirements", "course_includes")}),
    )

admin.site.register(Module, ModuleAdmin)
admin.site.register(Lesson)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Enrollment)
admin.site.register(LessonProgress)
admin.site.register(AssignmentSubmission)
