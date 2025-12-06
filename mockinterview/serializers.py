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
        date = attrs.get("scheduled_date")
        time = attrs.get("scheduled_time")

        if date and time:
            # Create naive datetime
            scheduled_dt = datetime.datetime.combine(date, time)

            # Convert naive → aware
            if timezone.is_naive(scheduled_dt):
                scheduled_dt = timezone.make_aware(scheduled_dt)

            # Compare aware datetimes
            now = timezone.now()

            if scheduled_dt <= now:
                raise serializers.ValidationError(
                    "Scheduled date/time must be in the future."
                )

        return attrs
