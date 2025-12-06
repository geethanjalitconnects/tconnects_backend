# profiles/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

# ---------------------------
# Choice constants
# ---------------------------
EXPERIENCE_LEVEL_CHOICES = (
    ("fresher", "Fresher"),
    ("1_year", "1 year"),
    ("2_years", "2 years"),
    ("3_years", "3 years"),
    ("4_plus", "4+ years"),
)

PAYMENT_TYPE_CHOICES = (
    ("upi", "UPI"),
    ("bank_transfer", "Bank Transfer"),
)

# ---------------------------
# Candidate Profile
# ---------------------------

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="candidate_profile")
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default="fresher")
    skills = models.JSONField(default=list, blank=True)  # stores ["Python","React"]
    bio = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CandidateProfile: {self.user.email}"

    class Meta:
        verbose_name = "Candidate Profile"
        verbose_name_plural = "Candidate Profiles"


# ---------------------------
# Recruiter (Basic) Profile
# ---------------------------

class RecruiterBasicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="recruiter_basic")
    full_name = models.CharField(max_length=255, blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    position_in_company = models.CharField(max_length=255, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RecruiterBasic: {self.user.email}"

    class Meta:
        verbose_name = "Recruiter Basic Profile"
        verbose_name_plural = "Recruiter Basic Profiles"


# ---------------------------
# Company Profile (no logo for now)
# ---------------------------

class CompanyProfile(models.Model):
    recruiter = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company_profile")
    company_name = models.CharField(max_length=255)
    industry_category = models.CharField(max_length=255, blank=True, null=True)
    company_size = models.CharField(max_length=100, blank=True, null=True)  # e.g., "1-10", "100-500"
    company_location = models.CharField(max_length=255, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    about_company = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profiles"


# ---------------------------
# Freelancer models
# ---------------------------

class FreelancerBasicInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="freelancer_basic")
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    languages_known = models.JSONField(default=list, blank=True)  # e.g. ["English","Hindi"]
    profile_picture = models.ImageField(upload_to="freelancer_pictures/", blank=True, null=True)

    # ✅ ADD HERE
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"FreelancerBasic: {self.user.email}"

    class Meta:
        verbose_name = "Freelancer Basic Info"
        verbose_name_plural = "Freelancer Basic Infos"



class FreelancerProfessionalDetails(models.Model):
    freelancer = models.OneToOneField(FreelancerBasicInfo, on_delete=models.CASCADE, related_name="professional_details")
    area_of_expertise = models.CharField(max_length=255, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    job_category = models.CharField(max_length=255, blank=True, null=True)
    professional_bio = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ProfessionalDetails: {self.freelancer.user.email}"


class FreelancerEducation(models.Model):
    freelancer = models.ForeignKey(FreelancerBasicInfo, on_delete=models.CASCADE, related_name="education")
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    start_year = models.PositiveSmallIntegerField(blank=True, null=True)
    end_year = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.degree} @ {self.institution} ({self.freelancer.user.email})"


class FreelancerAvailability(models.Model):
    freelancer = models.OneToOneField(FreelancerBasicInfo, on_delete=models.CASCADE, related_name="availability")
    is_available = models.BooleanField(default=True)
    is_occupied = models.BooleanField(default=False)
    available_from = models.TimeField(blank=True, null=True)
    available_to = models.TimeField(blank=True, null=True)
    time_zone = models.CharField(max_length=100, blank=True, null=True)
    available_days = models.JSONField(default=list, blank=True)  # ["Mon","Tue",...]
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Availability: {self.freelancer.user.email}"


class FreelancerPaymentMethod(models.Model):
    freelancer = models.ForeignKey(
        FreelancerBasicInfo,
        on_delete=models.CASCADE,
        related_name="payment_methods"
    )
    payment_type = models.CharField(max_length=50)  # e.g. "UPI" or "Bank Transfer"

    # UPI FIELD
    upi_id = models.CharField(max_length=255, blank=True, null=True)

    # BANK FIELDS
    account_number = models.CharField(max_length=50, blank=True, null=True)  # rename to match serializer
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)      # ⭐ NEW FIELD

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment Method for {self.freelancer.full_name}"



class FreelancerSocialLinks(models.Model):
    freelancer = models.OneToOneField(
        FreelancerBasicInfo,
        on_delete=models.CASCADE,
        related_name="social_links"
    )
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)

    # Existing rating field
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    # ⭐ IMPORTANT — Add these fields
    ratings = models.JSONField(default=list, blank=True)  # Example: [{"stars":5,"comment":"Great!"}]
    badges = models.JSONField(default=list, blank=True)   # Example: ["Top Rated", "Verified"]

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Social Links for {self.freelancer.full_name}"
