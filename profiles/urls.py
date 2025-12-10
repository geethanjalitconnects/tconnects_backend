# profiles/urls.py

from django.urls import path
from .views import (
    # Candidate
    CandidateProfileView,
    CandidateResumeUploadView,
    CandidateProfilePictureUploadView,

    # Recruiter
    RecruiterBasicProfileView,
    CompanyProfileView,
    PublicCompanyProfileView,

    # Freelancer
    FreelancerBasicInfoView,
    FreelancerProfilePictureUploadView,
    FreelancerProfessionalDetailsView,
    FreelancerEducationListCreateView,
    FreelancerEducationUpdateDeleteView,
    FreelancerAvailabilityView,
    FreelancerPaymentMethodListCreateView,
    FreelancerPaymentMethodDeleteView,
    FreelancerSocialLinksView,
    FreelancerProfilePreviewView,
    FreelancerPublishProfileView,
    DeleteFreelancerProfileView,
    
    # Public Freelancer Views
    FreelancerPublicListView,
    FreelancerPublicDetailView,
)

urlpatterns = [
    # ================================
    # CANDIDATE PROFILE ROUTES
    # ================================
    path("candidate/me/", CandidateProfileView.as_view(), name="candidate-profile"),
    path("candidate/upload-resume/", CandidateResumeUploadView.as_view(), name="candidate-upload-resume"),
    path("candidate/upload-profile-picture/", CandidateProfilePictureUploadView.as_view(), name="candidate-upload-picture"),

    # ================================
    # RECRUITER PROFILE ROUTES
    # ================================
    path("recruiter/basic/", RecruiterBasicProfileView.as_view(), name="recruiter-basic-profile"),
    path("recruiter/company/", CompanyProfileView.as_view(), name="company-profile"),
    path("company/<int:recruiter_id>/", PublicCompanyProfileView.as_view(), name="public-company-profile"),

    # ================================
    # FREELANCER PROFILE ROUTES (AUTHENTICATED)
    # ================================
    path("freelancer/basic/", FreelancerBasicInfoView.as_view(), name="freelancer-basic"),
    path("freelancer/upload-picture/", FreelancerProfilePictureUploadView.as_view(), name="freelancer-upload-picture"),
    path("freelancer/professional-details/", FreelancerProfessionalDetailsView.as_view(), name="freelancer-professional"),
    path("freelancer/education/", FreelancerEducationListCreateView.as_view(), name="freelancer-education-list-create"),
    path("freelancer/education/<int:pk>/", FreelancerEducationUpdateDeleteView.as_view(), name="freelancer-education-update-delete"),
    path("freelancer/availability/", FreelancerAvailabilityView.as_view(), name="freelancer-availability"),
    path("freelancer/payment-methods/", FreelancerPaymentMethodListCreateView.as_view(), name="freelancer-payments"),
    path("freelancer/payment-methods/<int:pk>/", FreelancerPaymentMethodDeleteView.as_view(), name="freelancer-payment-delete"),
    path("freelancer/social-links/", FreelancerSocialLinksView.as_view(), name="freelancer-social"),
    path("freelancer/preview/", FreelancerProfilePreviewView.as_view(), name="freelancer-preview"),
    path("freelancer/publish/", FreelancerPublishProfileView.as_view(), name="freelancer-publish"),
    path("freelancer/delete/", DeleteFreelancerProfileView.as_view(), name="freelancer-delete"),

    # ================================
    # PUBLIC FREELANCER ROUTES (NO AUTH REQUIRED)
    # ================================
    path("freelancers/", FreelancerPublicListView.as_view(), name="freelancer-public-list"),
    path("freelancers/<int:pk>/", FreelancerPublicDetailView.as_view(), name="freelancer-public-detail"),
]