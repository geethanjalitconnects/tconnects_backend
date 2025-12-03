# applications/views.py — FINAL CLEAN VERSION

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, generics
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView
)

from .models import JobApplication, InternshipApplication, SavedJob, SavedInternship
from .serializers import (
    JobApplicationCreateSerializer,
    JobApplicationSerializer,
    JobApplicationStatusUpdateSerializer,

    InternshipApplicationCreateSerializer,
    InternshipApplicationSerializer,
    InternshipApplicationStatusUpdateSerializer,

    SavedJobSerializer,
    SavedInternshipSerializer,
)
from jobs.models import Job
from internships.models import Internship


# ============================================================
# PERMISSIONS
# ============================================================

class IsCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "candidate"


class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "recruiter"


# ============================================================
# CANDIDATE — APPLY FOR JOB
# ============================================================

class ApplyJobView(CreateAPIView):
    permission_classes = [IsCandidate]
    serializer_class = JobApplicationCreateSerializer


# ============================================================
# CANDIDATE — APPLY FOR INTERNSHIP
# ============================================================

class ApplyInternshipView(CreateAPIView):
    permission_classes = [IsCandidate]
    serializer_class = InternshipApplicationCreateSerializer


# ============================================================
# CANDIDATE — VIEW APPLIED JOBS
# ============================================================

class CandidateAppliedJobsView(ListAPIView):
    permission_classes = [IsCandidate]
    serializer_class = JobApplicationSerializer

    def get_queryset(self):
        return JobApplication.objects.filter(
            candidate=self.request.user
        ).order_by("-created_at")


# ============================================================
# CANDIDATE — VIEW APPLIED INTERNSHIPS
# ============================================================

class CandidateAppliedInternshipsView(ListAPIView):
    permission_classes = [IsCandidate]
    serializer_class = InternshipApplicationSerializer

    def get_queryset(self):
        return InternshipApplication.objects.filter(
            candidate=self.request.user
        ).order_by("-created_at")


# ============================================================
# RECRUITER — VIEW JOB APPLICANTS
# ============================================================

class RecruiterJobApplicantsView(ListAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = JobApplicationSerializer

    def get_queryset(self):
        job_id = self.kwargs["job_id"]
        return JobApplication.objects.filter(
            job__id=job_id,
            job__recruiter=self.request.user
        ).order_by("-created_at")


# ============================================================
# RECRUITER — VIEW INTERNSHIP APPLICANTS
# ============================================================

class RecruiterInternshipApplicantsView(ListAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = InternshipApplicationSerializer

    def get_queryset(self):
        internship_id = self.kwargs["internship_id"]
        return InternshipApplication.objects.filter(
            internship__id=internship_id,
            internship__recruiter=self.request.user
        ).order_by("-created_at")


# ============================================================
# RECRUITER — UPDATE JOB APPLICATION STATUS
# ============================================================

class UpdateJobApplicationStatusView(UpdateAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = JobApplicationStatusUpdateSerializer
    lookup_field = "id"

    def get_queryset(self):
        return JobApplication.objects.filter(job__recruiter=self.request.user)


# ============================================================
# RECRUITER — UPDATE INTERNSHIP APPLICATION STATUS
# ============================================================

class UpdateInternshipApplicationStatusView(UpdateAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = InternshipApplicationStatusUpdateSerializer
    lookup_field = "id"

    def get_queryset(self):
        return InternshipApplication.objects.filter(
            internship__recruiter=self.request.user
        )


# ============================================================
# SAVED JOBS
# ============================================================

class SavedJobsListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(
            user=self.request.user
        ).select_related("job")


class AddSavedJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SavedJobSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        job = serializer.validated_data["job"]

        saved, created = SavedJob.objects.get_or_create(
            user=request.user,
            job=job
        )

        return Response(
            SavedJobSerializer(saved).data,
            status=201 if created else 200
        )


class RemoveSavedJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, job_id):
        saved = SavedJob.objects.filter(
            user=request.user,
            job__id=job_id
        ).first()

        if not saved:
            return Response({"detail": "Not found"}, status=404)

        saved.delete()
        return Response(status=204)


# ============================================================
# SAVED INTERNSHIPS (FIXED)
# ============================================================

class SavedInternshipsListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedInternshipSerializer

    def get_queryset(self):
        return SavedInternship.objects.filter(
            candidate=self.request.user
        ).select_related("internship")


class AddSavedInternshipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SavedInternshipSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        internship = serializer.validated_data["internship"]

        saved, created = SavedInternship.objects.get_or_create(
            candidate=request.user,
            internship=internship
        )

        return Response(
            SavedInternshipSerializer(saved).data,
            status=201 if created else 200
        )


class RemoveSavedInternshipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, internship_id):
        saved = SavedInternship.objects.filter(
            candidate=request.user,
            internship__id=internship_id
        ).first()

        if not saved:
            return Response({"detail": "Not found"}, status=404)

        saved.delete()
        return Response(status=204)
