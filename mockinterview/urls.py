from django.urls import path
from .views import MockInterviewScheduleView, MyUpcomingMockInterviewsView

urlpatterns = [
    path("schedule/", MockInterviewScheduleView.as_view(), name="mock-schedule"),
    path("my-interviews/", MyUpcomingMockInterviewsView.as_view(), name="mock-my-interviews"),
]
