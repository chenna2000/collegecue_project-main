from django import forms # type: ignore
from .models import Job, Application, Company, Resume

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['job_title', 'company', 'location', 'description', 'requirements', 'job_type', 'experience', 'category', 'skills', 'experience_yr', 'workplaceTypes','questions']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['candidate_name', 'email', 'phone_number', 'resume', 'cover_letter', 'skills']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'city', 'state', 'country_name', 'website', 'sector_type' ,'description']

class ResumeForm(forms.ModelForm):
    class Meta:
       model = Resume
       fields = ['name', 'email', 'phone', 'summary', 'experience', 'education', 'skills','certifications','academic_projects']

