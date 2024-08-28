from django.contrib import admin # type: ignore
from .models import  CandidateStatus_rejected, CandidateStatus_under_review, Job, Application, Company, CandidateStatus_selected, CandidateStatus_not_eligible,Resume


admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Company)
admin.site.register(CandidateStatus_selected)
admin.site.register(CandidateStatus_rejected)
admin.site.register(CandidateStatus_not_eligible)
admin.site.register(CandidateStatus_under_review)
admin.site.register(Resume)



