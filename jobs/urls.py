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
    # SEO SLUG URL (MUST BE FIRST!!)
    # ================================
    path("<slug:slug>/", JobDetailView.as_view(), name="job-detail-slug"),

    # ================================
    # NORMAL ID URL (FALLBACK)
    # ================================
    path("<int:id>/", JobDetailView.as_view(), name="job-detail"),

    # ================================
    # PUBLIC JOB LIST
    # ================================
    path("", JobListView.as_view(), name="job-list"),

    # ================================
    # RECRUITER ENDPOINTS
    # ================================
    path("create/", JobCreateView.as_view(), name="job-create"),
    path("<int:id>/update/", JobUpdateView.as_view(), name="job-update"),
    path("<int:id>/delete/", JobDeleteView.as_view(), name="job-delete"),
    path("my-jobs/", RecruiterJobListView.as_view(), name="recruiter-job-list"),
]
