from django import forms # type: ignore
from .models import Subscriber1,new_user,Consultant,Forgot2,UniversityInCharge,Subscriber,Verify,Forgot,CompanyInCharge

class CompanyInChargeForm(forms.ModelForm):
    class Meta:
        model = CompanyInCharge
        fields = '__all__'

class UniversityInChargeForm(forms.ModelForm):
    class Meta:
        model = UniversityInCharge
        fields = '__all__'

class ConsultantForm(forms.ModelForm):
    class Meta:
        model = Consultant
        fields = '__all__'

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'})
}

class ForgotForm(forms.ModelForm):
    class Meta:
        model = Forgot
        fields = ['email']

class VerifyForm(forms.ModelForm):
    class Meta:
        model = Verify
        fields = ['otp']

class Forgot2Form(forms.ModelForm):
    class Meta:
        model = Forgot2
        fields = '__all__'

class LoginForm(forms.ModelForm):
    class Meta:
        model = new_user
        fields =['email','password']

class SubscriptionForm1(forms.ModelForm):
    class Meta:
        model = Subscriber1
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'})
}