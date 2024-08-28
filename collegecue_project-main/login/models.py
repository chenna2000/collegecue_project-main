from django.contrib.auth.models import AbstractUser # type: ignore
from django.db import models # type: ignore

class CustomUser(AbstractUser):
    is_subadmin = models.BooleanField(default=False)
    groups = models.ManyToManyField('auth.Group', related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_set', blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.is_superuser:
            self.is_subadmin = True
        super().save(*args, **kwargs)

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.email} generated at {self.timestamp}"

class new_user(models.Model):
    firstname=models.CharField(max_length=20)
    lastname=models.CharField(max_length=20)
    country_code=models.CharField(max_length=5,default='IN')
    phonenumber=models.CharField(max_length=10)
    email=models.EmailField()
    password=models.CharField(max_length=100)
    course=models.CharField(max_length=50,default='')
    education=models.CharField(max_length=20,default='Not specified')
    percentage=models.CharField(max_length=10,default='0')
    preferred_destination=models.CharField(max_length=20,default='Not specified')
    start_date = models.CharField(max_length=4)
    entrance=models.CharField(max_length=5,default='N/A')
    passport=models.CharField(max_length=5,default='None')
    mode_study=models.CharField(max_length=20,default='None')

class Meta:
    db_table="collegecuefinal_data"

class CompanyInCharge(models.Model):
    company_name = models.CharField(max_length=255,default="null")
    official_email = models.EmailField(unique=True,default="Null")
    country_code = models.CharField(max_length=3, default='+91')
    mobile_number = models.CharField(max_length=15,default="Null")
    password = models.CharField(max_length=128,default="null")
    linkedin_profile = models.URLField(blank=True, null=True)
    company_person_name = models.CharField(max_length=255,default="Null")
    agreed_to_terms = models.BooleanField(default=False)

class UniversityInCharge(models.Model):
    university_name = models.CharField(max_length=255)
    official_email = models.EmailField(unique=True,default="Null")
    country_code = models.CharField(max_length=3, default='+91')
    mobile_number = models.CharField(max_length=15,default="Null")
    password = models.CharField(max_length=128,default="null")
    linkedin_profile = models.URLField(blank=True, null=True)
    college_person_name = models.CharField(max_length=255,default="Null")
    agreed_to_terms = models.BooleanField(default=False)

class Consultant(models.Model):
    consultant_name = models.CharField(max_length=255,default="Null")
    official_email = models.EmailField(unique=True,default="Null")
    country_code = models.CharField(max_length=3, default='+91')
    mobile_number = models.CharField(max_length=15,default="Null")
    password = models.CharField(max_length=128,default="null")
    linkedin_profile = models.URLField(blank=True, null=True)
    consultant_person_name = models.CharField(max_length=255,default="Null")
    agreed_to_terms = models.BooleanField(default=False)

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.email

class Forgot(models.Model):
    email = models.EmailField(unique=False)

class Verify(models.Model):
    otp=models.CharField(max_length=4)

class Forgot2(models.Model):
    password=models.CharField(max_length=12)
    confirm_password=models.CharField(max_length=12)

class Subscriber1(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

class User(models.Model):
    google_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    picture = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
      return self.email