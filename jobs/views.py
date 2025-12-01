# jobs/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView
)
from django.db.models import Q

from .models import Job
from .serializers import (
    JobListSerializer,
    JobDetailSerializer,
    JobCreateUpdateSerializer
)

# ======================================================
# ROLE PERMISSIONS
# ======================================================

class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "recruiter"


# ======================================================
# PUBLIC JOB LIST (JobsListPage.jsx)
# ======================================================

class JobListView(ListAPIView):
    """
    GET /api/jobs/
    Supports filters:
    - ?search=python
    - ?location=Chennai
    - ?category=Risk Management
    - ?employment_type=full_time
    """
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobListSerializer

    def get_queryset(self):
        qs = Job.objects.filter(is_active=True)

        search = self.request.query_params.get("search")
        location = self.request.query_params.get("location")
        category = self.request.query_params.get("category")
        employment_type = self.request.query_params.get("employment_type")

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

        if employment_type:
            qs = qs.filter(employment_type=employment_type)

        return qs.order_by("-created_at")


# ======================================================
# PUBLIC JOB DETAILS (JobDetailsPage.jsx)
# ======================================================

class JobDetailView(RetrieveAPIView):
    """
    GET /api/jobs/<id>/
    """
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobDetailSerializer
    lookup_field = "id"


# ======================================================
# RECRUITER — CREATE JOB
# ======================================================

class JobCreateView(CreateAPIView):
    """
    POST /api/jobs/create/
    Recruiter creates a job.
    """
    permission_classes = [IsRecruiter]
    serializer_class = JobCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user)


# ======================================================
# RECRUITER — UPDATE JOB
# ======================================================

class JobUpdateView(UpdateAPIView):
    """
    PATCH /api/jobs/<id>/update/
    Only the recruiter who created the job can update it.
    """
    permission_classes = [IsRecruiter]
    serializer_class = JobCreateUpdateSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user)


# ======================================================
# RECRUITER — DELETE JOB
# ======================================================

class JobDeleteView(DestroyAPIView):
    """
    DELETE /api/jobs/<id>/delete/
    Only the recruiter who created the job can delete it.
    """
    permission_classes = [IsRecruiter]
    lookup_field = "id"

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user)


# ======================================================
# RECRUITER — LIST MY JOBS (Recruiter Dashboard)
# ======================================================

class RecruiterJobListView(ListAPIView):
    """
    GET /api/jobs/my-jobs/
    Returns all jobs posted by the recruiter.
    """
    permission_classes = [IsRecruiter]
    serializer_class = JobListSerializer

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user).order_by("-created_at")
