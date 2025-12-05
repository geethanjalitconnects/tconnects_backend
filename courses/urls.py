from django.urls import path
from . import views

urlpatterns = [
    path("", views.CourseListAPIView.as_view(), name="courses-list"),

    # Course detail
    path("<int:id>/", views.CourseDetailAPIView.as_view(), name="course-detail-by-id"),
    path("<slug:slug>/<int:id>/", views.CourseDetailAPIView.as_view(), name="course-detail"),

    # Learn page
    path("<slug:slug>/<int:id>/learn/", views.course_learn_view, name="course-learn"),

    # Enroll (ONLY ONE — correct one)
    path("<int:id>/enroll/", views.enroll_course_view, name="course-enroll"),

    # Check enrolled
    path("<int:id>/is-enrolled/", views.check_is_enrolled, name="course-is-enrolled"),

    # Lesson complete
    path("lesson/<int:lesson_id>/complete/", views.lesson_complete_view, name="lesson-complete"),

    # Assignment submit
    path("assignment/<int:assignment_id>/submit/", views.assignment_submit_view, name="assignment-submit"),

    # Dashboard → my courses
    path("my-courses/", views.my_courses_view, name="my-courses"),
]
