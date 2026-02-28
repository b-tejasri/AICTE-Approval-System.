from django.db import models
from django.utils import timezone
import uuid 

from django.contrib.auth.models import User


from django.contrib.auth.hashers import make_password, check_password

class DemoTable(models.Model):
    name = models.CharField(max_length = 255)
    aicte_id = models.CharField(max_length= 100)


class Institution(models.Model):
    institution_name = models.CharField(max_length=255)
    aicte_id         = models.CharField(max_length=100, blank=True, default='')
    inst_type        = models.CharField(max_length=100, default='Engineering')
    category         = models.CharField(max_length=100, default='Affiliated')
    year_established = models.IntegerField(default=2000)
    affiliated_univ  = models.CharField(max_length=255, blank=True, default='')
    state            = models.CharField(max_length=100, default='')
    district         = models.CharField(max_length=100, default='')
    pincode          = models.CharField(max_length=10, blank=True, default='')
    principal_name   = models.CharField(max_length=255, blank=True, default='')
    email            = models.EmailField(unique=True)
    mobile           = models.CharField(max_length=20, blank=True, default='')
    password         = models.CharField(max_length=255)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    # Overall approval status for the institution
    APPROVAL_STATUS = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('resubmitted', 'Resubmitted'),
    ]
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')

    def set_password(self, raw):
        self.password = make_password(raw)

    def check_password(self, raw):
        return check_password(raw, self.password)

    def __str__(self):
        return self.institution_name


class DisclosureSection(models.Model):
    SECTION_CHOICES = [
        ('faculty',        'Faculty Details'),
        ('labs',           'Laboratory Details'),
        ('infrastructure', 'Infrastructure'),
        ('students',       'Student Details'),
        ('financials',     'Financial Details'),
        ('accreditation',  'Accreditation'),
    ]

    institution    = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='disclosures')
    section_type   = models.CharField(max_length=50, choices=SECTION_CHOICES)
    academic_year  = models.CharField(max_length=20, default='2024-25')
    pdf_file       = models.FileField(upload_to='disclosure_pdfs/')
    extracted_text = models.TextField(blank=True, default='')
    ai_response    = models.JSONField(default=dict)
    uploaded_at    = models.DateTimeField(auto_now_add=True)
    status         = models.CharField(max_length=30, default='Analyzed')

    # Section-level approval tracking
    SECTION_STATUS = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    review_status = models.CharField(max_length=20, choices=SECTION_STATUS, default='pending')
    review_notes  = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.institution} - {self.section_type} ({self.academic_year})"


class InstitutionData(models.Model):
    institution = models.OneToOneField(Institution, on_delete=models.CASCADE, related_name='data')

    # Faculty
    total_faculty     = models.IntegerField(default=0)
    required_faculty  = models.IntegerField(default=0)
    faculty_phd_count = models.IntegerField(default=0)
    faculty_details   = models.JSONField(default=list)

    # Labs
    total_labs  = models.IntegerField(default=0)
    lab_details = models.JSONField(default=list)

    # Infrastructure
    total_classrooms = models.IntegerField(default=0)
    library_books    = models.IntegerField(default=0)
    computer_count   = models.IntegerField(default=0)
    total_area_sqft  = models.IntegerField(default=0)
    hostel_capacity  = models.IntegerField(default=0)

    # Students
    total_students  = models.IntegerField(default=0)
    ug_students     = models.IntegerField(default=0)
    pg_students     = models.IntegerField(default=0)
    programs_offered = models.JSONField(default=list)

    # Financials
    annual_budget = models.FloatField(default=0.0)
    fee_structure = models.JSONField(default=dict)

    # Accreditation
    naac_grade    = models.CharField(max_length=10, blank=True, default='')
    nba_programs  = models.CharField(max_length=10000,blank=True, default='')
    iso_certified = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Data — {self.institution}"


class AIRiskAnalysis(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE,
                                    related_name='risk_analyses', null=True, blank=True)
    section     = models.ForeignKey(DisclosureSection, on_delete=models.CASCADE,
                                    related_name='risk', null=True, blank=True)

    risk_score     = models.IntegerField(default=0)
    risk_level     = models.CharField(max_length=20, default='Low')
    compliance_pct = models.FloatField(default=100.0)

    faculty_shortage = models.BooleanField(default=False)
    infra_deficit    = models.BooleanField(default=False)
    expired_certs    = models.BooleanField(default=False)
    faculty_ratio    = models.FloatField(default=0.0)

    risk_factors = models.JSONField(default=list)
    suggestions  = models.JSONField(default=list)

    # Per-section scores for detailed breakdown
    section_scores = models.JSONField(default=dict)

    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-analyzed_at']

    def __str__(self):
        return f"{self.institution} — {self.risk_level} ({self.risk_score})"


class ApprovalRequest(models.Model):
    """
    Tracks the approval workflow:
    Institution submits → Authority reviews → Approves or Rejects → Institution notified.
    """
    STATUS_CHOICES = [
        ('submitted',  'Submitted for Review'),
        ('under_review', 'Under Review'),
        ('approved',   'Approved'),
        ('rejected',   'Rejected'),
        ('resubmitted','Resubmitted'),
    ]

    institution      = models.ForeignKey(Institution, on_delete=models.CASCADE,
                                          related_name='approval_requests')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at     = models.DateTimeField(auto_now_add=True)
    reviewed_at      = models.DateTimeField(null=True, blank=True)
    reviewed_by      = models.CharField(max_length=255, blank=True, default='AICTE Authority')
    authority_notes  = models.TextField(blank=True, default='')

    # Snapshot of risk at time of submission
    risk_score_at_submission  = models.IntegerField(default=0)
    risk_level_at_submission  = models.CharField(max_length=20, default='')
    risk_factors_at_submission = models.JSONField(default=list)

    # Sections uploaded at time of submission
    sections_submitted = models.JSONField(default=list)

    # Per-section review decisions by authority
    section_decisions = models.JSONField(default=dict)   # {section_type: {status, notes}}

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.institution} — {self.status} ({self.submitted_at.date()})"


class Notification(models.Model):
    TYPES = [('warning','Warning'),('success','Success'),('danger','Danger'),('info','Info')]
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='notifications')
    title       = models.CharField(max_length=255)
    message     = models.TextField()
    notif_type  = models.CharField(max_length=20, choices=TYPES, default='info')
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.institution} — {self.title}"
