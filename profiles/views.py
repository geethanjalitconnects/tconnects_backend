# profiles/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
)
from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model

from .models import (
    CandidateProfile,
    RecruiterBasicProfile,
    CompanyProfile,
    FreelancerBasicInfo,
    FreelancerProfessionalDetails,
    FreelancerEducation,
    FreelancerAvailability,
    FreelancerPaymentMethod,
    FreelancerSocialLinks,
)

from .serializers import (
    CandidateProfileSerializer,
    CandidateResumeUploadSerializer,
    CandidateProfilePictureSerializer,

    RecruiterBasicProfileSerializer,
    CompanyProfileSerializer,

    FreelancerBasicInfoSerializer,
    FreelancerProfilePictureUploadSerializer,
    FreelancerProfessionalDetailsSerializer,
    FreelancerEducationSerializer,
    FreelancerAvailabilitySerializer,
    FreelancerPaymentMethodSerializer,
    FreelancerSocialLinksSerializer,
    FreelancerProfilePreviewSerializer,
)

User = get_user_model()

# ============================================================
# PERMISSIONS
# ============================================================

class IsCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "candidate"


class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "recruiter"


class IsFreelancer(permissions.BasePermission):
    """
    Your requirement: Every candidate is also a freelancer.
    So freelancer access is allowed if role == candidate.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "candidate"


# ============================================================
# CANDIDATE PROFILE
# ============================================================

class CandidateProfileView(RetrieveUpdateAPIView):
    """
    GET /api/profiles/candidate/me/
    PATCH /api/profiles/candidate/me/
    """
    permission_classes = [IsCandidate]
    serializer_class = CandidateProfileSerializer

    def get_object(self):
        # Auto-create if not exists
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return profile


class CandidateResumeUploadView(APIView):
    """
    POST /api/profiles/candidate/upload-resume/
    multipart/form-data: resume=FILE
    """
    permission_classes = [IsCandidate]

    def post(self, request):
        profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
        serializer = CandidateResumeUploadSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"resume_url": profile.resume.url}, status=200)

        return Response(serializer.errors, status=400)


class CandidateProfilePictureUploadView(APIView):
    """
    POST /api/profiles/candidate/upload-profile-picture/
    """
    permission_classes = [IsCandidate]

    def post(self, request):
        profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
        serializer = CandidateProfilePictureSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"profile_picture": profile.profile_picture.url}, status=200)

        return Response(serializer.errors, status=400)


# ============================================================
# RECRUITER BASIC PROFILE
# ============================================================

class RecruiterBasicProfileView(RetrieveUpdateAPIView):
    """
    GET /api/profiles/recruiter/basic/
    PATCH /api/profiles/recruiter/basic/
    """
    permission_classes = [IsRecruiter]
    serializer_class = RecruiterBasicProfileSerializer

    def get_object(self):
        profile, _ = RecruiterBasicProfile.objects.get_or_create(user=self.request.user)
        return profile


# ============================================================
# COMPANY PROFILE (Recruiter)
# ============================================================

class CompanyProfileView(RetrieveUpdateAPIView):
    """
    GET /api/profiles/recruiter/company/
    PATCH /api/profiles/recruiter/company/
    """
    permission_classes = [IsRecruiter]
    serializer_class = CompanyProfileSerializer

    def get_object(self):
        profile, _ = CompanyProfile.objects.get_or_create(recruiter=self.request.user)
        return profile


# Public endpoint to view a company by recruiter ID
class PublicCompanyProfileView(APIView):
    """
    GET /api/profiles/company/<recruiter_id>/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, recruiter_id):
        recruiter = get_object_or_404(User, id=recruiter_id)
        company = getattr(recruiter, "company_profile", None)

        if not company:
            return Response({"detail": "Company profile not found"}, status=404)

        serializer = CompanyProfileSerializer(company)
        return Response(serializer.data, status=200)


# ============================================================
# FREELANCER BASIC INFO
# ============================================================

class FreelancerBasicInfoView(RetrieveUpdateAPIView):
    """
    GET /api/profiles/freelancer/basic/
    PATCH /api/profiles/freelancer/basic/
    """
    permission_classes = [IsFreelancer]
    serializer_class = FreelancerBasicInfoSerializer

    def get_object(self):
        profile, _ = FreelancerBasicInfo.objects.get_or_create(user=self.request.user)
        return profile


class FreelancerProfilePictureUploadView(APIView):
    permission_classes = [IsFreelancer]

    def post(self, request):
        profile, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        serializer = FreelancerProfilePictureUploadSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"profile_picture": profile.profile_picture.url}, status=200)

        return Response(serializer.errors, status=400)


# ============================================================
# FREELANCER PROFESSIONAL DETAILS
# ============================================================

class FreelancerProfessionalDetailsView(RetrieveUpdateAPIView):
    permission_classes = [IsFreelancer]
    serializer_class = FreelancerProfessionalDetailsSerializer

    def get_object(self):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=self.request.user)
        details, _ = FreelancerProfessionalDetails.objects.get_or_create(freelancer=basic)
        return details


# ============================================================
# FREELANCER EDUCATION (CRUD)
# ============================================================

class FreelancerEducationListCreateView(APIView):
    permission_classes = [IsFreelancer]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        education = basic.education.all()
        serializer = FreelancerEducationSerializer(education, many=True)
        return Response(serializer.data)

    def post(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        serializer = FreelancerEducationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(freelancer=basic)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class FreelancerEducationUpdateDeleteView(APIView):
    permission_classes = [IsFreelancer]

    def patch(self, request, pk):
        edu = get_object_or_404(FreelancerEducation, id=pk, freelancer__user=request.user)
        serializer = FreelancerEducationSerializer(edu, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        edu = get_object_or_404(FreelancerEducation, id=pk, freelancer__user=request.user)
        edu.delete()
        return Response({"detail": "Deleted"}, status=204)


# ============================================================
# FREELANCER AVAILABILITY
# ============================================================

class FreelancerAvailabilityView(RetrieveUpdateAPIView):
    permission_classes = [IsFreelancer]
    serializer_class = FreelancerAvailabilitySerializer

    def get_object(self):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=self.request.user)
        availability, _ = FreelancerAvailability.objects.get_or_create(freelancer=basic)
        return availability


# ============================================================
# FREELANCER PAYMENT METHODS (ADD / LIST / DELETE)
# ============================================================

class FreelancerPaymentMethodListCreateView(APIView):
    permission_classes = [IsFreelancer]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        payments = basic.payment_methods.all()
        serializer = FreelancerPaymentMethodSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        serializer = FreelancerPaymentMethodSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(freelancer=basic)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class FreelancerPaymentMethodDeleteView(DestroyAPIView):
    permission_classes = [IsFreelancer]
    serializer_class = FreelancerPaymentMethodSerializer

    def get_queryset(self):
        return FreelancerPaymentMethod.objects.filter(freelancer__user=self.request.user)


# ============================================================
# FREELANCER SOCIAL LINKS
# ============================================================

class FreelancerSocialLinksView(RetrieveUpdateAPIView):
    permission_classes = [IsFreelancer]
    serializer_class = FreelancerSocialLinksSerializer

    def get_object(self):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=self.request.user)
        links, _ = FreelancerSocialLinks.objects.get_or_create(freelancer=basic)
        return links


# ============================================================
# FREELANCER PROFILE PREVIEW (MERGED)
# ============================================================

class FreelancerProfilePreviewView(APIView):
    permission_classes = [IsFreelancer]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        professional, _ = FreelancerProfessionalDetails.objects.get_or_create(freelancer=basic)
        availability, _ = FreelancerAvailability.objects.get_or_create(freelancer=basic)
        links, _ = FreelancerSocialLinks.objects.get_or_create(freelancer=basic)
        education = basic.education.all()
        payments = basic.payment_methods.all()

        serializer = FreelancerProfilePreviewSerializer({
            "basic_info": basic,
            "professional_details": professional,
            "education": education,
            "availability": availability,
            "payment_methods": payments,
            "social_links": links,
        })

        return Response(serializer.data, status=200)
    
class FreelancerPublishProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            basic = FreelancerBasicInfo.objects.get(user=request.user)
        except FreelancerBasicInfo.DoesNotExist:
            return Response({"error": "Basic info not completed"}, status=400)

        basic.is_published = True
        basic.save()

        return Response({"message": "Profile published successfully"}, status=200)

# ============================================================
# PUBLIC FREELANCER LIST (VISIBLE TO RECRUITERS)
# ============================================================

class FreelancerPublicListView(ListAPIView):
    """
    GET /api/profiles/freelancers/
    Returns ONLY published freelancers
    """
    serializer_class = FreelancerBasicInfoSerializer
    permission_classes = [permissions.AllowAny]  # Recruiters + public can view

    def get_queryset(self):
        return FreelancerBasicInfo.objects.filter(is_published=True)

class FreelancerPublicDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            basic = FreelancerBasicInfo.objects.get(id=pk, is_published=True)
        except FreelancerBasicInfo.DoesNotExist:
            return Response({"error": "Freelancer not found"}, status=404)

        # PROFESSIONAL DETAILS
        professional = FreelancerProfessionalDetails.objects.filter(
            freelancer=basic
        ).first()

        # EDUCATION
        education = FreelancerEducation.objects.filter(
            freelancer=basic
        )

        # AVAILABILITY
        availability = FreelancerAvailability.objects.filter(
            freelancer=basic
        ).first()

        # PAYMENT METHODS
        payments = FreelancerPaymentMethod.objects.filter(
            freelancer=basic
        )

        # SOCIAL LINKS
        social = FreelancerSocialLinks.objects.filter(
            freelancer=basic
        ).first()

        # RATINGS stored inside SocialLinks JSON field
        ratings = social.ratings if social and social.ratings else []
        badges = social.badges if social and social.badges else []

        return Response({
            "basic": FreelancerBasicInfoSerializer(basic).data,
            "professional": FreelancerProfessionalDetailsSerializer(professional).data if professional else None,
            "education": FreelancerEducationSerializer(education, many=True).data,
            "availability": FreelancerAvailabilitySerializer(availability).data if availability else None,
            "payments": FreelancerPaymentMethodSerializer(payments, many=True).data,
            "social": FreelancerSocialLinksSerializer(social).data if social else None,
            "ratings": ratings,
            "badges": badges,
        })
