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

# ----------------------------------------------------
# FREELANCER PROFILE VIEWS (FULLY FIXED + STABLE)
# ----------------------------------------------------



# ----------------------------------------
# BASIC INFO
# ----------------------------------------
class FreelancerBasicInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        return Response(FreelancerBasicInfoSerializer(basic).data)

    def patch(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        serializer = FreelancerBasicInfoSerializer(basic, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ----------------------------------------
# PROFILE PICTURE UPLOAD
# ----------------------------------------
class FreelancerProfilePictureUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        picture = request.FILES.get("profile_picture")

        if not picture:
            return Response({"error": "No file provided"}, status=400)

        basic.profile_picture = picture
        basic.save()
        return Response({"message": "Profile picture updated successfully"})


# ----------------------------------------
# PROFESSIONAL DETAILS
# ----------------------------------------
class FreelancerProfessionalDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        details, _ = FreelancerProfessionalDetails.objects.get_or_create(freelancer=basic)
        return Response(FreelancerProfessionalDetailsSerializer(details).data)

    def patch(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        details, _ = FreelancerProfessionalDetails.objects.get_or_create(freelancer=basic)

        serializer = FreelancerProfessionalDetailsSerializer(details, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


# ----------------------------------------
# EDUCATION LIST + CREATE
# ----------------------------------------
class FreelancerEducationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        education = FreelancerEducation.objects.filter(freelancer=basic)
        return Response(FreelancerEducationSerializer(education, many=True).data)

    def post(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        serializer = FreelancerEducationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(freelancer=basic)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# ----------------------------------------
# EDUCATION UPDATE + DELETE
# ----------------------------------------
class FreelancerEducationUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            record = FreelancerEducation.objects.get(pk=pk, freelancer__user=request.user)
        except FreelancerEducation.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = FreelancerEducationSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            record = FreelancerEducation.objects.get(pk=pk, freelancer__user=request.user)
        except FreelancerEducation.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        record.delete()
        return Response({"message": "Deleted successfully"}, status=200)


# ----------------------------------------
# AVAILABILITY
# ----------------------------------------
class FreelancerAvailabilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        availability, _ = FreelancerAvailability.objects.get_or_create(freelancer=basic)
        return Response(FreelancerAvailabilitySerializer(availability).data)

    def patch(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        availability, _ = FreelancerAvailability.objects.get_or_create(freelancer=basic)

        serializer = FreelancerAvailabilitySerializer(availability, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


# ----------------------------------------
# PAYMENT METHODS
# ----------------------------------------
class FreelancerPaymentMethodListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        methods = FreelancerPaymentMethod.objects.filter(freelancer=basic)
        return Response(FreelancerPaymentMethodSerializer(methods, many=True).data)

    def post(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        serializer = FreelancerPaymentMethodSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(freelancer=basic)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class FreelancerPaymentMethodDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            method = FreelancerPaymentMethod.objects.get(pk=pk, freelancer__user=request.user)
        except FreelancerPaymentMethod.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        method.delete()
        return Response({"message": "Deleted successfully"}, status=200)


# ----------------------------------------
# SOCIAL LINKS
# ----------------------------------------
class FreelancerSocialLinksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        links, _ = FreelancerSocialLinks.objects.get_or_create(freelancer=basic)
        return Response(FreelancerSocialLinksSerializer(links).data)

    def patch(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        links, _ = FreelancerSocialLinks.objects.get_or_create(freelancer=basic)

        serializer = FreelancerSocialLinksSerializer(links, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


# ----------------------------------------
# PROFILE PREVIEW (CENTRAL API)
# ----------------------------------------
class FreelancerProfilePreviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        professional, _ = FreelancerProfessionalDetails.objects.get_or_create(freelancer=basic)
        availability, _ = FreelancerAvailability.objects.get_or_create(freelancer=basic)
        links, _ = FreelancerSocialLinks.objects.get_or_create(freelancer=basic)

        education = FreelancerEducation.objects.filter(freelancer=basic)
        payments = FreelancerPaymentMethod.objects.filter(freelancer=basic)

        ratings = links.ratings if hasattr(links, "ratings") else []
        badges = links.badges if hasattr(links, "badges") else []

        return Response({
            "basic": FreelancerBasicInfoSerializer(basic).data,
            "professional": FreelancerProfessionalDetailsSerializer(professional).data,
            "education": FreelancerEducationSerializer(education, many=True).data,
            "availability": FreelancerAvailabilitySerializer(availability).data,
            "payments": FreelancerPaymentMethodSerializer(payments, many=True).data,
            "social": FreelancerSocialLinksSerializer(links).data,
            "ratings": ratings,
            "badges": badges,
        })

# ----------------------------------------
# PUBLISH PROFILE
# ----------------------------------------
class FreelancerPublishProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        basic, _ = FreelancerBasicInfo.objects.get_or_create(user=request.user)
        basic.is_published = True
        basic.save()
        return Response({"message": "Freelancer profile published successfully"})


# ----------------------------------------
# PUBLIC LIST + PUBLIC DETAIL
# ----------------------------------------
class FreelancerPublicListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        freelancers = FreelancerBasicInfo.objects.filter(is_published=True)
        return Response(FreelancerBasicInfoSerializer(freelancers, many=True).data)


class FreelancerPublicDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            basic = FreelancerBasicInfo.objects.get(id=pk, is_published=True)
        except FreelancerBasicInfo.DoesNotExist:
            return Response({"error": "Freelancer not found"}, status=404)

        professional = FreelancerProfessionalDetails.objects.filter(freelancer=basic).first()
        availability = FreelancerAvailability.objects.filter(freelancer=basic).first()
        education = FreelancerEducation.objects.filter(freelancer=basic)
        payments = FreelancerPaymentMethod.objects.filter(freelancer=basic)
        social = FreelancerSocialLinks.objects.filter(freelancer=basic).first()

        ratings = social.ratings if social and hasattr(social, "ratings") else []
        badges = social.badges if social and hasattr(social, "badges") else []

        return Response({
            "basic": FreelancerBasicInfoSerializer(basic).data,
            "professional": FreelancerProfessionalDetailsSerializer(professional).data if professional else None,
            "availability": FreelancerAvailabilitySerializer(availability).data if availability else None,
            "education": FreelancerEducationSerializer(education, many=True).data,
            "payments": FreelancerPaymentMethodSerializer(payments, many=True).data,
            "social": FreelancerSocialLinksSerializer(social).data if social else None,
            "ratings": ratings,
            "badges": badges,
        })
