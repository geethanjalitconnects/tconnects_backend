# mockinterview/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import MockInterviewSerializer
from .models import MockInterview
from django.utils import timezone
from django.db.models import Q

class MockInterviewScheduleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        serializer = MockInterviewSerializer(data=data)
        if serializer.is_valid():
            # set user then save
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyUpcomingMockInterviewsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # return upcoming interviews (scheduled datetime >= now)
        now = timezone.now()
        # filter by combining date & time; simplest approach: compare date > today OR (date == today and time >= now.time())
        from django.db.models import F

        interviews = MockInterview.objects.filter(
            user=request.user
        ).filter(
            Q(scheduled_date__gt=now.date()) |
            Q(scheduled_date=now.date(), scheduled_time__gte=now.time())
        ).order_by("scheduled_date", "scheduled_time")

        serializer = MockInterviewSerializer(interviews, many=True)
        return Response(serializer.data)
