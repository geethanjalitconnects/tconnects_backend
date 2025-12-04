from django.urls import path
from . import views

urlpatterns = [
    path("", views.CourseListAPIView.as_view(), name="courses-list"),
    path("<int:id>/", views.CourseDetailAPIView.as_view(), name="course-detail-by-id"),
    path("<slug:slug>/<int:id>/", views.CourseDetailAPIView.as_view(), name="course-detail"),
    path("<slug:slug>/<int:id>/learn/", views.course_learn_view, name="course-learn"),
    path("<int:id>/enroll/", views.enroll_course_view, name="course-enroll"),
    path("lesson/<int:lesson_id>/complete/", views.lesson_complete_view, name="lesson-complete"),
    path("assignment/<int:assignment_id>/submit/", views.assignment_submit_view, name="assignment-submit"),
]
