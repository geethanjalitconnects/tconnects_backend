# internships/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView
)
from django.db.models import Q

from .models import Internship
from .serializers import (
    InternshipListSerializer,
    InternshipDetailSerializer,
    InternshipCreateUpdateSerializer
)
import logging
from accounts.permissions import IsRecruiter

logger = logging.getLogger(__name__)


# ======================================================
# ROLE PERMISSIONS
# ======================================================

class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "recruiter"


# ======================================================
# PUBLIC INTERNSHIP LIST (InternshipsListPage.jsx)
# ======================================================

class InternshipListView(ListAPIView):
    """
    GET /api/internships/
    Supports filters:
    - ?search=sql
    - ?location=Chennai
    - ?category=Risk Management
    - ?internship_type=remote
    """
    queryset = Internship.objects.filter(is_active=True)
    serializer_class = InternshipListSerializer

    def get_queryset(self):
        qs = Internship.objects.filter(is_active=True)

        search = self.request.query_params.get("search")
        location = self.request.query_params.get("location")
        category = self.request.query_params.get("category")
        internship_type = self.request.query_params.get("internship_type")

        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(company_name__icontains=search)
                | Q(short_description__icontains=search)
            )

        if location:
            qs = qs.filter(location__icontains=location)

        if category:
            qs = qs.filter(category__icontains=category)

        if internship_type:
            qs = qs.filter(internship_type=internship_type)

        return qs.order_by("-created_at")


# ======================================================
# PUBLIC INTERNSHIP DETAILS (InternshipDetailsPage.jsx)
# ======================================================

class InternshipDetailView(RetrieveAPIView):
    """
    GET /api/internships/<id>/
    """
    queryset = Internship.objects.filter(is_active=True)
    serializer_class = InternshipDetailSerializer
    lookup_field = "id"


# ======================================================
# RECRUITER — CREATE INTERNSHIP
# ======================================================

class InternshipCreateView(CreateAPIView):
    queryset = Internship.objects.all()
    serializer_class = InternshipCreateUpdateSerializer
    permission_classes = [IsRecruiter]  # only recruiters can create

    def perform_create(self, serializer):
        # Attach recruiter to the internship posting
        serializer.save(recruiter=self.request.user)




# ======================================================
# RECRUITER — UPDATE INTERNSHIP
# ======================================================

class InternshipUpdateView(UpdateAPIView):
    """
    PATCH /api/internships/<id>/update/
    Only the recruiter who posted can edit.
    """
    permission_classes = [IsRecruiter]
    serializer_class = InternshipCreateUpdateSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Internship.objects.filter(recruiter=self.request.user)


# ======================================================
# RECRUITER — DELETE INTERNSHIP
# ======================================================

class InternshipDeleteView(DestroyAPIView):
    """
    DELETE /api/internships/<id>/delete/
    """
    permission_classes = [IsRecruiter]
    lookup_field = "id"

    def get_queryset(self):
        return Internship.objects.filter(recruiter=self.request.user)


# ======================================================
# RECRUITER — LIST MY INTERNSHIPS
# ======================================================

class RecruiterInternshipListView(ListAPIView):
    """
    GET /api/internships/my-internships/
    Shows internships posted by recruiter.
    """
    permission_classes = [IsRecruiter]
    serializer_class = InternshipListSerializer

    def get_queryset(self):
        return Internship.objects.filter(
            recruiter=self.request.user
        ).order_by("-created_at")
