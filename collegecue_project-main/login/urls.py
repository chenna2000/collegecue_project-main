from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register',views.Register.as_view(),name='register'),
    path('next',views.Next.as_view(),name="next"),
    path('login',views.Login.as_view(),name="login"),
    path('forgot',views.Forgot_view.as_view(),name="forgot"),
    path('forgot2',views.Forgot2_view.as_view(),name="forgot2"),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('register/company/', views.RegisterCompanyInChargeView.as_view(), name='register_company_incharge_api'),
    path('register/university/', views.RegisterUniversityInChargeView.as_view(), name='register_university_incharge_api'),
    path('register/consultant/', views.RegisterConsultantView.as_view(), name='register_consultant_incharge_api'),
    path('search/', views.search, name='search'),
    path('job_portal', views.Subscriber_view.as_view(), name='job_portal'),
    path('subscriber', views.Subscriber_view1.as_view(), name='subscriber'),
    path('verify_otp1',views.Verify_view.as_view(),name="verify_otp1"),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('verify-token/', views.verify_token, name='verify_token'),
]