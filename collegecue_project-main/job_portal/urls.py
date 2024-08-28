from django.urls import path # type: ignore
from . import views
from .views import  CustomObtainAuthToken,  CompanyListCreateView, CompanyDetailView

urlpatterns = [
    path('home', views.home, name='home'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('applications/<int:job_id>/', views.job_applications, name='job_applications'),
    path('job-status/<int:job_id>/', views.job_status, name='job_status'),
    path('companies/', CompanyListCreateView.as_view(), name='company_list_create'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('find_status/', views.find_status, name="find_status"),
    path('candidate_profile/', views.candidate_profile, name ="candidate_profile"),
    path('company_status/<str:status_choice>/', views.company_status, name= "company_status"),
    path('create/', views.create_resume, name='create_resume'),
    path('<int:pk>/', views.resume_detail, name='resume_detail'),
    path('category_with_count/', views.count_jobs_by_category, name='category_with_count'),
    path('fetch_jobs/', views.fetch_jobs_by_exp_skills, name='fetch_jobs'),
    path('fetch_jobs_category/', views.fetch_jobs_by_category_location_skills, name='fetch_jobs_category'),
    path('get_job_titles/', views.fetch_job_titles, name='get_job_titles'),
    path('get_job_types/', views.fetch_job_types, name='get_job_types'),
    path('get_job_experince/', views.fetch_job_experience, name='get_job_experince'),
    path('get_job_category/', views.fetch_job_category, name='get_job_category'),
    path('get_job_workplaceTypes/', views.fetch_job_workplaceTypes, name='get_job_workplaceTypes'),
    path('get_job_location/', views.fetch_job_location, name='get_job_location'),
    path('fetch_sector_types/', views.fetch_sector_types, name='fetch_sector_types'),
    path('fetch_contry_types/', views.fetch_contry_types, name='fetch_contry_types'),
    path('fetch_status/', views.fetch_status_choices, name='fetch_status'),
    path('api-token-auth/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
]
