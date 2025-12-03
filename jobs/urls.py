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
    # SEO friendly URL – MUST COME FIRST
    path("<slug:slug>/", JobDetailView.as_view(), name="job-detail-slug"),

    # ID fallback URL
    path("<int:id>/", JobDetailView.as_view(), name="job-detail"),

    # Other routes
    path("", JobListView.as_view(), name="job-list"),
    path("create/", JobCreateView.as_view(), name="job-create"),
    path("<int:id>/update/", JobUpdateView.as_view(), name="job-update"),
    path("<int:id>/delete/", JobDeleteView.as_view(), name="job-delete"),
    path("my-jobs/", RecruiterJobListView.as_view(), name="recruiter-job-list"),
]
