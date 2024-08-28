from django.shortcuts import get_object_or_404 # type: ignore
from django.http import HttpResponseBadRequest, JsonResponse # type: ignore
from django.middleware.csrf import get_token # type: ignore
from django.views.decorators.csrf import csrf_exempt, csrf_protect # type: ignore
from django.utils import timezone # type: ignore
from django.db.models import Q # type: ignore
from rest_framework.response import Response # type: ignore
from .models import CandidateStatus_rejected, CandidateStatus_under_review, Job, Application, Company, CandidateStatus_selected,CandidateStatus_not_eligible, Resume
from .forms import CompanyForm, JobForm, ApplicationForm, ResumeForm
import json
from datetime import timedelta
from django.utils.decorators import method_decorator # type: ignore
from django.views import View # type: ignore
from rest_framework.authtoken.views import ObtainAuthToken # type: ignore
from rest_framework.authtoken.models import Token # type: ignore
from rest_framework import status # type: ignore


def home(request):
    return JsonResponse({"message": "Welcome to CollegeCue!"}, status=200)

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token}, status=200)

@csrf_protect
def job_list(request):
    try:
        if request.method == 'GET':
            search_query = request.GET.get('search', '')
            job_title = request.GET.get('job_title', '')
            sort_order = request.GET.get('sort', '')
            job_type = request.GET.get('job_type', '')
            company_name = request.GET.get('company', '')
            experience_level = request.GET.get('experience', '')
            explore_new_jobs = request.GET.get('explore_new_jobs', '')
            category = request.GET.get('category', '')
            skills = request.GET.get('skills', '')
            workplaceTypes = request.GET.get('workplaceTypes', '')
            jobs = Job.objects.all()

            if search_query:
                jobs = jobs.filter(Q(job_title__icontains=search_query))
            if company_name:
                jobs = jobs.filter(Q(company__icontains=company_name))
            if job_title:
                jobs = jobs.filter(Q(job_title__icontains=job_title))
            if job_type:
                jobs = jobs.filter(Q(job_type__icontains=job_type))
            if experience_level:
                jobs = jobs.filter(Q(experience__icontains=experience_level))
            if category:
                jobs = jobs.filter(Q(category__icontains=category))
            if workplaceTypes:
                jobs = jobs.filter(Q(workplaceTypes__icontains=workplaceTypes))
            if skills:
                skills_list = skills.split(',')
                for skill in skills_list:
                    jobs = jobs.filter(Q(skills__icontains=skill))
            if explore_new_jobs:
                days = 7 if explore_new_jobs == 'week' else 30
                start_date = timezone.now() - timedelta(days=days)
                jobs = jobs.filter(published_at__gte=start_date)
            if sort_order:
                jobs = jobs.order_by(sort_order)

            jobs_list = [{
                'id': job.id,
                'job_title': job.job_title,
                'company': job.company,
                'location': job.location,
                'requirements': job.requirements,
                'job_type': job.job_type,
                'experience': job.experience,
                'category': job.category,
                'published_at': job.published_at,
                'skills': job.skills,
                'workplaceTypes': job.workplaceTypes,
                'questions': job.questions,
            } for job in jobs]
            return JsonResponse(jobs_list, safe=False, status=200)

        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)

            count_jobs_company = Job.objects.filter(company=data['company']).count()
            if count_jobs_company >= 100:
                return JsonResponse({'message': 'Limit exceeded for job postings by this company'}, status=200)

            job_skills = data.get('skills', '')
            if job_skills:
                job_list = job_skills.split(', ')
                unique_job_list = list(set(job_list))
                job_skills_str = ', '.join(unique_job_list)
                data['skills'] = job_skills_str

            form = JobForm(data)
            if form.is_valid():
                job = form.save()
                return JsonResponse({'message': 'Job created successfully', 'job_id': job.id}, status=201)
            return JsonResponse({'errors': form.errors}, status=400)

        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_protect
def job_detail(request, job_id):
    try:
        job = get_object_or_404(Job, id=job_id)
        if request.method == 'GET':
            return JsonResponse({
                'id': job.id,
                'title': job.job_title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'requirements': job.requirements,
                'job_type': job.job_type,
                'experience': job.experience,
                'category': job.category,
                'published_at': job.published_at
            })

        elif request.method == 'PUT':
            data = json.loads(request.body)
            form = JobForm(data, instance=job)
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Job updated successfully'}, status=200)
            return JsonResponse({'errors': form.errors}, status=400)

        elif request.method == 'DELETE':
            job.delete()
            return JsonResponse({'message': 'Job deleted successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def apply_job(request, job_id):
    try:
        json_data = json.loads(request.POST.get('data'))
        job = get_object_or_404(Job, id=job_id)
        if request.method == 'POST':
            form = ApplicationForm(json_data, request.FILES)
            if form.is_valid():
                application = form.save(commit=False)
                application.job = job
                job_skills = set(job.skills.split(', '))
                candidate_skills = set(application.skills.split(', '))
                cand_skills = ', '.join(candidate_skills)
                application.skills = cand_skills

                if not job_skills.intersection(candidate_skills):
                    return JsonResponse({'message': 'Candidate is not eligible to apply'}, status=404)

                application.save()
                return JsonResponse({'message': 'Application submitted successfully', 'application_id': application.id}, status=201)
            return JsonResponse({'errors': form.errors}, status=400)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_protect
def job_applications(request, job_id):
    try:
        job = get_object_or_404(Job, id=job_id)
        applications = Application.objects.filter(job=job)
        applications_list = [{
            'id': app.id,
            'candidate_name': app.candidate_name,
            'email': app.email,
            'phone_number': app.phone_number,
            'resume_url': app.resume.url if app.resume else '',
            'cover_letter': app.cover_letter,
            'status': app.status,
            'applied_at': app.applied_at,
        } for app in applications]
        return JsonResponse(applications_list, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def job_status(request, job_id):
    try:
        pending_applications = Application.objects.filter(job_id=job_id, status='pending')
        pending_count = pending_applications.count()

        return JsonResponse({
            'job_id': job_id,
            'pending_count': pending_count
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CompanyListCreateView(View):
    def get(self, request):
        try:
            companies = list(Company.objects.all().values())
            return JsonResponse(companies, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)
            form = CompanyForm(data)
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Company Created Successfully'}, status=201)
            else:
                return JsonResponse(form.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CompanyDetailView(View):
    def get(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            return JsonResponse({
                "id": company.id,
                "name": company.name,
                "address": company.address,
                "city": company.city,
                "state": company.state,
                "country": company.country_name,
                "website": company.website
            })
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def put(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            data = json.loads(request.body)
            form = CompanyForm(data, instance=company)
            if form.is_valid():
                company = form.save()
                return JsonResponse({'message': 'Company Updated successfully'}, status=200)
            else:
                return JsonResponse(form.errors, status=400)
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            company.delete()
            return JsonResponse({'message': 'Company deleted successfully'}, status=200)
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def find_status(request):
    try:
        co_name = request.GET['name']
        job_ids = Job.objects.filter(company=co_name)
        applications = Application.objects.filter(job__in=job_ids)
        statuses = {}
        for application in applications:
            if application.status not in statuses:
                statuses[application.status] = 1
            else:
                statuses[application.status] += 1
        return JsonResponse({'message': statuses}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def candidate_profile(request):
    try:
        json_data = json.loads(request.POST.get('data'))
        skills_can = json_data['skills']
        can_skills_set = set(skills_can.split(', '))
        skills_of_can = ', '.join(can_skills_set)
        print(skills_of_can)
        can_location = json_data['location']
        experience_year = json_data['experience_years']
        print(experience_year)
        matching_jobs = []
        all_jobs = Job.objects.all()
        for job in all_jobs:
            job_skills_set = set(job.skills.split(', '))
            ex_year_arr = job.experience_yr.split('-')
            print(ex_year_arr)
            if can_skills_set.intersection(job_skills_set) and experience_year >= int(ex_year_arr[0]) and experience_year <= int(ex_year_arr[1]) and job.location == can_location:
                matching_jobs.append({
                    "id": job.id,
                    "title": job.job_title,
                    "company": job.company,
                    "experience_year": job.experience_yr,
                    "location": job.location,
                })

        return JsonResponse({'matching_jobs': matching_jobs})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def company_status(request, status_choice):
    try:
        co_name = request.GET['name']
        job_id = Job.objects.filter(company=co_name)
        apply_id = Application.objects.filter(job__in=job_id)
        name = []
        if status_choice == 'selected':
            candidate_status_modelname = CandidateStatus_selected
        elif status_choice == 'rejected':
            candidate_status_modelname = CandidateStatus_rejected
        elif status_choice == 'not_eligible':
            candidate_status_modelname = CandidateStatus_not_eligible
        elif status_choice == 'under_review':
            candidate_status_modelname = CandidateStatus_under_review
        for application in apply_id:
            if application.status == status_choice:
                name.append(application.candidate_name)
                candidate_status_modelname.objects.create(
                    candidate_name=application.candidate_name,
                    status=status_choice,
                    company_name=co_name,
                    job_id=application.job_id
                )

        return JsonResponse({'message': name}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def create_resume(request):
    try:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                form = ResumeForm(data)
                if form.is_valid():
                    resume = form.save()
                    return JsonResponse({'id': resume.id, 'message': 'Resume created successfully'}, status=200)
                else:
                    return JsonResponse({'errors': form.errors}, status=400)
            except json.JSONDecodeError:
                return HttpResponseBadRequest('Invalid JSON')
        else:
            return HttpResponseBadRequest('Invalid HTTP method')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def resume_detail(request, pk):
    try:
        if request.method == 'GET':
            resume = get_object_or_404(Resume, pk=pk)
            resume_data = {
                'id': resume.id,
                'name': resume.name,
                'email': resume.email,
                'phone': resume.phone,
                'summary': resume.summary,
                'experience': resume.experience,
                'education': resume.education,
                'skills': resume.skills,
                'certifications': resume.certifications,
                'academic_projects': resume.academic_projects,
            }
            return JsonResponse(resume_data, status=200)
        else:
            return HttpResponseBadRequest('Invalid HTTP method')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def count_jobs_by_category(request):
    if request.method == 'GET':
        category_counts = {}

        jobs = Job.objects.all()

        for job in jobs:
            if job.category in category_counts:
                category_counts[job.category] += 1
            else:
                category_counts[job.category] = 1

        response_data = [
            {'category': category, 'job_count': count}
            for category, count in category_counts.items()
        ]

        return JsonResponse({'category_counts': response_data}, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            if created:
                message = "New token created"
            else:
                message = "Existing token retrieved"
            return Response({
                'token': token.key,
                'username': user.username,
                 'message': message
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def fetch_jobs_by_exp_skills(request):
    if request.method == 'GET':
        experience = request.GET.get('experience')
        skills = request.GET.get('skills')

        skills_list = [skill.strip().lower() for skill in skills.split(',')] if skills else []

        jobs = Job.objects.all()

        if experience:
            jobs = jobs.filter(experience=experience)
            print(jobs)
        if skills_list:
            queries = Q()
            for skill in skills_list:
                queries |= Q(skills__icontains=skill)
                print(queries)
            jobs = jobs.filter(queries).distinct()
            print(jobs)

        if not (experience or skills_list):
            return JsonResponse({'error': 'Please enter at least one filter: category, location or skills.'}, status=400)

        job_list = []
        for job in jobs:
            job_list.append({
                'job_title': job.job_title,
                'company_name': job.company,
                'location': job.location,
                'workplaceType':job.workplaceTypes,
                'description':job.description,
                'requirements':job.requirements,
                'job_type':job.job_type,
                'experience': job.experience,
                'category':job.category,
                'required_skills': job.skills,
                'experience_yr':job.experience_yr,
            })

        return JsonResponse({'jobs': job_list}, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@csrf_exempt
def fetch_jobs_by_category_location_skills(request):
    if request.method == 'GET':
        category = request.GET.get('category')
        location = request.GET.get('location')
        skills = request.GET.get('skills')

        skills_list = [skill.strip().lower() for skill in skills.split(',')] if skills else []

        jobs = Job.objects.all()

        if category:
            jobs = jobs.filter(category=category)
        if location:
            jobs = jobs.filter(location=location)
        if skills_list:
            queries = Q()
            for skill in skills_list:
                queries |= Q(skills__icontains=skill)
            jobs = jobs.filter(queries).distinct()

        if not (category or location or skills_list):
            return JsonResponse({'error': 'Please enter at least one filter: category, location or skills.'}, status=400)

        job_list = []
        for job in jobs:
            job_list.append({
                'job_title': job.job_title,
                'company_name': job.company,
                'location': job.location,
                'workplaceType':job.workplaceTypes,
                'description':job.description,
                'requirements':job.requirements,
                'job_type':job.job_type,
                'experience': job.experience,
                'category':job.category,
                'required_skills': job.skills,
                'experience_yr':job.experience_yr,
            })

        return JsonResponse({'jobs': job_list}, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_job_titles(request):
    if request.method == 'GET':
        jobs = Job.objects.all()

        job_title = {
            job.job_title: job.job_title
            for job in jobs
            if job.job_title
        }
        return JsonResponse({'job_title': job_title})

def fetch_job_types(request):
    if request.method == 'GET':
        jobs = Job.objects.all()

        job_types = {
            job.job_type: job.job_type
            for job in jobs
            if job.job_type
        }
        return JsonResponse({'job_types': job_types})

def fetch_job_experience(request):
    if request.method == 'GET':
        jobs = Job.objects.all()

        exp_types = {
            job.experience: job.experience
            for job in jobs
            if job.experience
        }
        return JsonResponse({'exp_types': exp_types})

def fetch_job_category(request):
    if request.method == 'GET':
        jobs = Job.objects.all()

        category = {
            job.category: job.category
            for job in jobs
            if job.category
        }
        return JsonResponse({'category': category})

def fetch_job_workplaceTypes(request):
    if request.method == 'GET':
        jobs = Job.objects.all()

        workplaceTypes = {
            job.workplaceTypes: job.workplaceTypes
            for job in jobs
            if job.workplaceTypes
        }
        return JsonResponse({'workplaceTypes': workplaceTypes})

def fetch_job_location(request):
    if request.method == 'GET':
        jobs = Job.objects.all()

        location = {
            job.location: job.location
            for job in jobs
            if job.location
        }
        return JsonResponse({'location': location})

def fetch_sector_types(request):
    if request.method == 'GET':
        comapnies = Company.objects.all()

        sector_types = {
            company.sector_type: company.sector_type
            for company in comapnies
            if company.sector_type
        }
        return JsonResponse({'sector_type': sector_types})

def fetch_contry_types(request):
    if request.method == 'GET':
        comapnies = Company.objects.all()

        country_name = {
            company.country_name: company.country_name
            for company in comapnies
            if company.country_name
        }
        return JsonResponse({'country_name': country_name})

def fetch_status_choices(request):
    if request.method == 'GET':
        applications = Application.objects.all()

        status = {
            application.status: application.status
            for application in applications
            if application.status
        }
        return JsonResponse({'status': status})
