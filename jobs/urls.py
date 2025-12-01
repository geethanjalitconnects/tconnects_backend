# jobs/urls.py

from django.urls import path
from .views import (
    JobListView,
    JobDetailView,
    JobCreateView,
    JobUpdateView,
    JobDeleteView,
    RecruiterJobListView,
)

urlpatterns = [

    # ================================
    # PUBLIC ENDPOINTS
    # ================================
    path("", JobListView.as_view(), name="job-list"),
    path("<int:id>/", JobDetailView.as_view(), name="job-detail"),

    # ================================
    # RECRUITER ENDPOINTS
    # ================================
    path("create/", JobCreateView.as_view(), name="job-create"),
    path("<int:id>/update/", JobUpdateView.as_view(), name="job-update"),
    path("<int:id>/delete/", JobDeleteView.as_view(), name="job-delete"),

    # Recruiter dashboard — list jobs posted by this recruiter
    path("my-jobs/", RecruiterJobListView.as_view(), name="recruiter-job-list"),
]
