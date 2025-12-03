# applications/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView
)

from .models import JobApplication, InternshipApplication
from .serializers import (
    JobApplicationCreateSerializer,
    JobApplicationSerializer,
    JobApplicationStatusUpdateSerializer,

    InternshipApplicationCreateSerializer,
    InternshipApplicationSerializer,
    InternshipApplicationStatusUpdateSerializer,
)
from .models import SavedJob
from .serializers import SavedJobSerializer
from jobs.models import Job
from .models import SavedInternship
from .serializers import SavedInternshipSerializer
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
    """
    POST /api/applications/job/apply/
    { "job_id": 1, "cover_letter": "..." }
    """
    permission_classes = [IsCandidate]
    serializer_class = JobApplicationCreateSerializer


# ============================================================
# CANDIDATE — APPLY FOR INTERNSHIP
# ============================================================

class ApplyInternshipView(CreateAPIView):
    """
    POST /api/applications/internship/apply/
    { "internship_id": 1, "cover_letter": "..." }
    """
    permission_classes = [IsCandidate]
    serializer_class = InternshipApplicationCreateSerializer


# ============================================================
# CANDIDATE — VIEW APPLIED JOBS
# ============================================================

class CandidateAppliedJobsView(ListAPIView):
    """
    GET /api/applications/job/applied/
    Returns all job applications of candidate.
    """
    permission_classes = [IsCandidate]
    serializer_class = JobApplicationSerializer

    def get_queryset(self):
        return JobApplication.objects.filter(candidate=self.request.user).order_by("-created_at")


# ============================================================
# CANDIDATE — VIEW APPLIED INTERNSHIPS
# ============================================================

class CandidateAppliedInternshipsView(ListAPIView):
    """
    GET /api/applications/internship/applied/
    """
    permission_classes = [IsCandidate]
    serializer_class = InternshipApplicationSerializer

    def get_queryset(self):
        return InternshipApplication.objects.filter(candidate=self.request.user).order_by("-created_at")


# ============================================================
# RECRUITER — VIEW JOB APPLICANTS
# ============================================================

class RecruiterJobApplicantsView(ListAPIView):
    """
    GET /api/applications/job/<job_id>/applicants/
    Only recruiter who posted the job can view applicants.
    """
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
    """
    GET /api/applications/internship/<internship_id>/applicants/
    """
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
    """
    PATCH /api/applications/job/<id>/status/
    { "status": "shortlisted" }
    """
    permission_classes = [IsRecruiter]
    serializer_class = JobApplicationStatusUpdateSerializer
    lookup_field = "id"

    def get_queryset(self):
        # recruiter can update ONLY his own job's applications
        return JobApplication.objects.filter(job__recruiter=self.request.user)


# ============================================================
# RECRUITER — UPDATE INTERNSHIP APPLICATION STATUS
# ============================================================

class UpdateInternshipApplicationStatusView(UpdateAPIView):
    """
    PATCH /api/applications/internship/<id>/status/
    """
    permission_classes = [IsRecruiter]
    serializer_class = InternshipApplicationStatusUpdateSerializer
    lookup_field = "id"

    def get_queryset(self):
        return InternshipApplication.objects.filter(internship__recruiter=self.request.user)
class SavedJobsListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related("job")


class AddSavedJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SavedJobSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        job = serializer.validated_data["job"]

        saved, created = SavedJob.objects.get_or_create(
            user=request.user, job=job
        )

        if not created:
            return Response({"detail": "Job already saved."}, status=200)

        return Response(
            SavedJobSerializer(saved).data,
            status=status.HTTP_201_CREATED
        )


class RemoveSavedJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, job_id):
        saved = SavedJob.objects.filter(user=request.user, job__id=job_id).first()

        if not saved:
            return Response({"detail": "Not found."}, status=404)

        saved.delete()
        return Response({"detail": "Removed from saved jobs."}, status=204)
class SavedInternshipsListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedInternshipSerializer

    def get_queryset(self):
        return SavedInternship.objects.filter(
            user=self.request.user
        ).select_related("internship")
class AddSavedInternshipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SavedInternshipSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        internship = serializer.validated_data["internship"]

        saved, created = SavedInternship.objects.get_or_create(
            user=request.user,
            internship=internship
        )

        if not created:
            return Response({"detail": "Internship already saved."}, status=200)

        return Response(
            SavedInternshipSerializer(saved).data,
            status=status.HTTP_201_CREATED
        )
class RemoveSavedInternshipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, internship_id):
        saved_item = SavedInternship.objects.filter(
            user=request.user,
            internship__id=internship_id
        ).first()

        if not saved_item:
            return Response({"detail": "Not found."}, status=404)

        saved_item.delete()
        return Response({"detail": "Removed from saved internships."}, status=204)
