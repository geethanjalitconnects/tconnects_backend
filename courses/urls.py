from django.urls import path
from . import views

urlpatterns = [
    # List all courses
    path("", views.CourseListAPIView.as_view(), name="courses-list"),

    # Course details
    path("<slug:slug>/<int:id>/", views.CourseDetailAPIView.as_view(), name="course-detail"),

    # Learn page
    path("<slug:slug>/<int:id>/learn/", views.course_learn_view, name="course-learn"),

    # Enroll (ONLY correct one)
    path("<int:id>/enroll/", views.enroll_course_view, name="course-enroll"),

    # Check enrolled
    path("<int:id>/is-enrolled/", views.check_is_enrolled, name="course-is-enrolled"),

    # Mark lesson complete
    path("lesson/<int:lesson_id>/complete/", views.lesson_complete_view, name="lesson-complete"),

    # Submit assignment
    path("assignment/<int:assignment_id>/submit/", views.assignment_submit_view, name="assignment-submit"),

    # My courses (dashboard)
    path("my-courses/", views.my_courses_view, name="my-courses"),
]
