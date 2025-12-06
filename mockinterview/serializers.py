# mockinterview/serializers.py
from rest_framework import serializers
from .models import MockInterview
from django.utils import timezone
import datetime

class MockInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockInterview
        fields = [
            "id",
            "user",
            "job_role",
            "experience",
            "scheduled_date",
            "scheduled_time",
            "email",
            "interviewer_preference",
            "special_requests",
            "meeting_link",
            "created_at",
        ]
        read_only_fields = ("id", "user", "meeting_link", "created_at")

    def validate(self, attrs):
        # ensure scheduled datetime is in future
        date = attrs.get("scheduled_date")
        time = attrs.get("scheduled_time")
        if date and time:
            scheduled_dt = datetime.datetime.combine(date, time)
            # interpret as aware in server timezone
            if scheduled_dt <= timezone.now():
                raise serializers.ValidationError("Scheduled date/time must be in the future.")
        return attrs
