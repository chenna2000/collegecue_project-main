from django.db import models # type: ignore
from django.utils import timezone # type: ignore

class Job(models.Model):
    company = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    experience_yr = models.CharField(max_length=10, default="0-100")
    job_title = models.CharField(max_length=200)
    job_type = models.CharField(max_length=50)
    experience = models.CharField(max_length=50)
    category =models.CharField(max_length=100)
    skills = models.CharField(max_length=1000, blank= False, null=False)
    workplaceTypes = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    questions = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.job_title


class Application(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    candidate_name = models.CharField(max_length=255, null=False, default="Unknown Candidate")
    email = models.EmailField(null=False, default="unknown@example.com")
    phone_number = models.CharField(max_length=15, default="123-456-7890")
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(default="No cover letter provided")
    applied_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='pending')
    skills = models.CharField(max_length=1000, blank= False, null=False)

    def __str__(self):
        return f"{self.candidate_name} - {self.job.job_title}"

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    website = models.URLField()
    description = models.TextField(max_length=255,default='description')
    sector_type = models.CharField(max_length=100)
    country_name  = models.CharField(max_length=50)


    def _str_(self):
        return self.name

class Resume(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    summary = models.TextField()
    experience = models.TextField()
    education = models.TextField()
    skills = models.TextField()
    certifications = models.TextField(default='certifiations')
    academic_projects = models.TextField(default='academic_projects')

def __str__(self):
    return self.name

class CandidateStatus_selected(models.Model):
    candidate_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20,default='selected')
    company_name = models.CharField(max_length=255)
    job_id = models.IntegerField()

class CandidateStatus_rejected(models.Model):
    candidate_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20,default='rejected')
    company_name = models.CharField(max_length=255)
    job_id = models.IntegerField()

class CandidateStatus_not_eligible(models.Model):
    candidate_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20,default='not_eligible')
    company_name = models.CharField(max_length=255)
    job_id = models.IntegerField()

class CandidateStatus_under_review(models.Model):
    candidate_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20,default='under_review')
    company_name = models.CharField(max_length=255)
    job_id = models.IntegerField()