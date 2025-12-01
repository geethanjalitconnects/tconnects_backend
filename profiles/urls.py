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

    # Public company info (for job pages)
    path("company/<int:recruiter_id>/", PublicCompanyProfileView.as_view(), name="public-company-profile"),


    # ================================
    # FREELANCER PROFILE ROUTES
    # ================================
    
    # Basic info
    path("freelancer/basic/", FreelancerBasicInfoView.as_view(), name="freelancer-basic"),
    path("freelancer/upload-picture/", FreelancerProfilePictureUploadView.as_view(), name="freelancer-upload-picture"),

    # Professional details
    path("freelancer/professional-details/", FreelancerProfessionalDetailsView.as_view(), name="freelancer-professional"),

    # Education CRUD
    path("freelancer/education/", FreelancerEducationListCreateView.as_view(), name="freelancer-education-list-create"),
    path("freelancer/education/<int:pk>/", FreelancerEducationUpdateDeleteView.as_view(), name="freelancer-education-update-delete"),

    # Availability
    path("freelancer/availability/", FreelancerAvailabilityView.as_view(), name="freelancer-availability"),

    # Payment methods
    path("freelancer/payment-methods/", FreelancerPaymentMethodListCreateView.as_view(), name="freelancer-payments"),
    path("freelancer/payment-methods/<int:pk>/", FreelancerPaymentMethodDeleteView.as_view(), name="freelancer-payment-delete"),

    # Social links
    path("freelancer/social-links/", FreelancerSocialLinksView.as_view(), name="freelancer-social"),

    # Profile preview (merged)
    path("freelancer/preview/", FreelancerProfilePreviewView.as_view(), name="freelancer-preview"),
]
