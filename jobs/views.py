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
    queryset = Job.objects.filter(is_active=True)
    serializer_class = JobDetailSerializer
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        slug = kwargs.get("slug", None)

        if slug:
            try:
                job_id = int(slug.split("-")[-1])  # last part = actual ID
                self.kwargs["id"] = job_id
            except:
                return Response({"error": "Invalid job URL"}, status=400)

        return super().get(request, *args, **kwargs)




# ======================================================
# RECRUITER — CREATE JOB
# ======================================================

class JobCreateView(CreateAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = JobCreateUpdateSerializer

    def perform_create(self, serializer):
        # DO NOT pass recruiter here. Serializer handles recruiter.
        serializer.save()


# ======================================================
# RECRUITER — UPDATE JOB
# ======================================================

class JobUpdateView(UpdateAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = JobCreateUpdateSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user)


# ======================================================
# RECRUITER — DELETE JOB
# ======================================================

class JobDeleteView(DestroyAPIView):
    permission_classes = [IsRecruiter]
    lookup_field = "id"

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user)


# ======================================================
# RECRUITER — LIST MY JOBS (Recruiter Dashboard)
# ======================================================

class RecruiterJobListView(ListAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = JobListSerializer

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user).order_by("-created_at")
