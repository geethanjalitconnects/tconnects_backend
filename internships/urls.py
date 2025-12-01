# internships/urls.py

from django.urls import path
from .views import (
    InternshipListView,
    InternshipDetailView,
    InternshipCreateView,
    InternshipUpdateView,
    InternshipDeleteView,
    RecruiterInternshipListView,
)

urlpatterns = [

    # ================================
    # PUBLIC ENDPOINTS
    # ================================
    path("", InternshipListView.as_view(), name="internship-list"),
    path("<int:id>/", InternshipDetailView.as_view(), name="internship-detail"),

    # ================================
    # RECRUITER ENDPOINTS
    # ================================
    path("create/", InternshipCreateView.as_view(), name="internship-create"),
    path("<int:id>/update/", InternshipUpdateView.as_view(), name="internship-update"),
    path("<int:id>/delete/", InternshipDeleteView.as_view(), name="internship-delete"),

    # Recruiter dashboard — list internships posted
    path("my-internships/", RecruiterInternshipListView.as_view(), name="recruiter-internship-list"),
]
