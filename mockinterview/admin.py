from django.contrib import admin
from .models import MockInterview

@admin.register(MockInterview)
class MockInterviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "job_role", "scheduled_date", "scheduled_time", "meeting_link")
    list_filter = ("scheduled_date",)
    search_fields = ("job_role", "email", "user__username", "user__email")
