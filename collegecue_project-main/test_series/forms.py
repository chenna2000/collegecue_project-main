from django import forms
from .models import ExamParticipant, ProctoringEvent

class StartProctoringSessionForm(forms.Form):
    exam_id = forms.IntegerField()
    duration = forms.DurationField(required=False, help_text="Duration of the session (e.g., '1:30:00' for 1 hour 30 minutes)")

class EndProctoringSessionForm(forms.Form):
    session_id = forms.IntegerField()

class RecordProctoringEventForm(forms.ModelForm):
    session_id = forms.IntegerField()

    class Meta:
        model = ProctoringEvent
        fields = ['event_type', 'details', 'session_id']

class SubmitAnswerForm(forms.Form):
    session_id = forms.IntegerField()
    question_no = forms.IntegerField()
    selected_option = forms.CharField(max_length=255)

class MarkForReviewForm(forms.Form):
    session_id = forms.IntegerField()
    question_no = forms.IntegerField()
    mark = forms.BooleanField()


class SubmitAllAnswersForm(forms.Form):
    session_id = forms.IntegerField()
    answers = forms.JSONField()

class ExamParticipantForm(forms.ModelForm):
    class Meta:
        model = ExamParticipant
        fields = ['name', 'email', 'phone_number']
