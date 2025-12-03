# applications/urls.py

from django.urls import path
from .views import (
    ApplyJobView,
    ApplyInternshipView,

    CandidateAppliedJobsView,
    CandidateAppliedInternshipsView,

    RecruiterJobApplicantsView,
    RecruiterInternshipApplicantsView,

    UpdateJobApplicationStatusView,
    UpdateInternshipApplicationStatusView
    
    
)
from .views import (
    SavedJobsListView,
    AddSavedJobView,
    RemoveSavedJobView
)
from .views import (
    SavedJobsListView,
    AddSavedJobView,
    RemoveSavedJobView,
    SavedInternshipsListView,
    AddSavedInternshipView,
    RemoveSavedInternshipView,
)
urlpatterns = [

    # ---------------------------------------------------------
    # CANDIDATE ACTIONS
    # ---------------------------------------------------------
    
    # Apply
    path("job/apply/", ApplyJobView.as_view(), name="apply-job"),
    path("internship/apply/", ApplyInternshipView.as_view(), name="apply-internship"),

    # Candidate applied lists
    path("job/applied/", CandidateAppliedJobsView.as_view(), name="candidate-applied-jobs"),
    path("internship/applied/", CandidateAppliedInternshipsView.as_view(), name="candidate-applied-internships"),


    # ---------------------------------------------------------
    # RECRUITER ACTIONS
    # ---------------------------------------------------------
    
    # View applicants
    path("job/<int:job_id>/applicants/", RecruiterJobApplicantsView.as_view(), name="recruiter-job-applicants"),
    path("internship/<int:internship_id>/applicants/", RecruiterInternshipApplicantsView.as_view(), name="recruiter-internship-applicants"),

    # Update status
    path("job/<int:id>/status/", UpdateJobApplicationStatusView.as_view(), name="update-job-application-status"),
    path("internship/<int:id>/status/", UpdateInternshipApplicationStatusView.as_view(), name="update-internship-application-status"),
    path("saved-jobs/", SavedJobsListView.as_view()),
    path("saved-jobs/add/", AddSavedJobView.as_view()),
    path("saved-jobs/remove/<int:job_id>/", RemoveSavedJobView.as_view()),
    
    path("saved-internships/", SavedInternshipsListView.as_view(), name="saved-internships"),
    path("saved-internships/add/", AddSavedInternshipView.as_view(), name="saved-internships-add"),
    path("saved-internships/remove/<int:internship_id>/", RemoveSavedInternshipView.as_view(), name="saved-internships-remove"),
    path("saved-internships/", SavedInternshipListCreateView.as_view(), name="saved-internships"),
    path("saved-internships/remove/<int:internship_id>/", SavedInternshipRemoveView.as_view(), name="remove-saved-internship"),

]
