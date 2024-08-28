from django.http import HttpResponse,JsonResponse # type: ignore
from django.core.mail import send_mail # type: ignore
from django.conf import settings # type: ignore
from django.middleware.csrf import get_token # type: ignore
from django.views.decorators.csrf import csrf_exempt, csrf_protect # type: ignore
from .utils import (send_data_to_google_sheet3,fetch_data_from_google_sheets,send_data_to_google_sheet4,
send_data_to_google_sheet2,send_data_to_google_sheets)
import secrets,json,requests,os # type: ignore
from .models import User, new_user
from django.contrib.auth.hashers import make_password, check_password # type: ignore
from django.utils.decorators import method_decorator # type: ignore
from django.views import View # type: ignore
from .forms import (UniversityInChargeForm,CompanyInChargeForm,ForgotForm,
LoginForm,SubscriptionForm1,ConsultantForm,Forgot2Form
,VerifyForm,SubscriptionForm)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # type: ignore
from google.oauth2 import id_token

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

def home(request):
    return HttpResponse("Welcome to CollegeCue!")

def get_csrf_token(request):
    csrf_token = get_token(request)

    return JsonResponse({'csrf_token': csrf_token})

@method_decorator(csrf_exempt, name='dispatch')
class Register(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))

        first_name = data.get('firstname')
        last_name = data.get('lastname')
        email= data.get('email')
        country_code= data.get('country_code')
        phone_number = data.get('phonenumber')
        password= data.get('password')
        if not email:
            return JsonResponse({'error': 'Please enter a correct email id'}, status=400)
        if not password:
            return JsonResponse({'error': 'Please enter password'}, status=400)

        hashed_password = make_password(password)
        send_data_to_google_sheets(first_name , last_name ,email ,country_code ,phone_number,hashed_password,"Sheet1")
        return JsonResponse({'message':'go to next page'})

@method_decorator(csrf_exempt, name='dispatch')
class Next(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        course = data.get('course')
        education = data.get('education')
        percentage = data.get('percentage')
        preferred_destination = data.get('preferred_destination')
        start_date = data.get('start_date')
        mode_study = data.get('mode_study')
        entrance_exam = data.get('entrance')
        passport = data.get('passport')
        country_code = data.get('country_code')
        phone_number = data.get('phonenumber')
        errors = {}
        if not entrance_exam:
            errors['entrance'] = 'Check box not clicked'
        if not passport:
            errors['passport'] = 'Check box not clicked'
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        us_data = fetch_data_from_google_sheets()
        if not us_data:
            return JsonResponse({'error': 'Failed to fetch data from Google Sheets'}, status=500)
        sheet = us_data[-1]
        us = new_user(
            firstname=sheet[0], lastname=sheet[1], email=sheet[2],
            country_code=country_code, phonenumber=phone_number,
            password=sheet[5], course=course, education=education,
            percentage=percentage, preferred_destination=preferred_destination,
            start_date=start_date, mode_study=mode_study,
            entrance=entrance_exam, passport=passport
        )
        us.save()
        return JsonResponse({'message': 'Registration successful'})


@method_decorator(csrf_exempt, name='dispatch')
class Login(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        form = LoginForm(data)
        if form.is_valid():
            email = data.get('email')
            password = data.get('password')
            if not email:
                return JsonResponse({'value_error': 'Please enter Email'}, status=400)

            if not password:
                return JsonResponse({'error': 'Please enter password'}, status=400)

            user = new_user.objects.filter(email=email).last()
            if not user:
                return JsonResponse({'error': 'Email id not found'}, status=404)
            if check_password(password, user.password):
                return JsonResponse({'message': 'Login successful'})
            else:
                return JsonResponse({'error': 'Invalid Credentials'}, status=400)
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class Forgot_view(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        form = ForgotForm(data)
        if form.is_valid():
            forgot=form.save()
            EMAIL=forgot.email
            user = new_user.objects.filter(email=EMAIL).first()
            if not user:
                return JsonResponse({'message':'This mail does not exists'})
            new_otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
            request.session['otp'] = new_otp
            request.session['email'] = EMAIL
            request.session.save()

            subject = 'Your New OTP'
            message = f'Your new OTP is: {new_otp}'
            sender_email = settings.EMAIL_HOST_USER
            recipient_email = [EMAIL]

            send_mail(subject, message, sender_email, recipient_email)
            return JsonResponse({'message':'otp sent successfully'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class Verify_view(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        form = VerifyForm(data)
        print(form.is_valid())
        if form.is_valid():
            verify=form.save()
            otp_entered=verify.otp
            stored_otp = request.session.get('otp')
            stored_email = request.session.get('email')

            if stored_email and stored_otp:
                if  stored_otp == otp_entered:
                    del request.session['otp']
                    return JsonResponse({'message': 'OTP verification successful'})
                else:
                    return JsonResponse({'error': 'Invalid OTP'}, status=400)
            else:
                return JsonResponse({'error': 'Session data not found'}, status=400)

@csrf_protect
def resend_otp(request):
    csrf_token = get_token(request)
    if not csrf_token:
        return JsonResponse({'error': 'CSRF token missing'}, status=403)
    email = request.session.get('email')
    new_otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
    request.session['otp'] = new_otp
    request.session['email'] = email
    subject = 'Your New OTP'
    message = f'Your new OTP is: {new_otp}'
    sender_email = settings.EMAIL_HOST_USER
    recipient_email = [email]
    send_mail(subject, message, sender_email, recipient_email)
    return JsonResponse({'message': 'New OTP sent successfully'})

@method_decorator(csrf_exempt, name='dispatch')
class Forgot2_view(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        form = Forgot2Form(data)
        print(form.is_valid())
        if form.is_valid():
            form.save(commit=False)
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            if password != confirm_password:
                return JsonResponse({'error': 'Passwords did not match'}, status=400)

            hashed_password = make_password(password)
            stored_email = request.session.get('email')
            user = new_user.objects.filter(email=stored_email).first()
            user.password=hashed_password
            user.save()

            del request.session['email']
            return JsonResponse({"message":'password updated successfully'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterCompanyInChargeView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': 'Invalid JSON'}, status=400)

        form = CompanyInChargeForm(data)
        if form.is_valid():
            company = form.save(commit=False)
            company.password = make_password(company.password)
            company.save()
            send_data_to_google_sheet2(
                company.company_name,
                company.official_email,
                company.country_code,
                company.mobile_number,
                company.password,
                company.linkedin_profile,
                company.company_person_name,
                company.agreed_to_terms,
                "Sheet2"
            )
            sender_email = settings.EMAIL_HOST_USER
            recipient_email = [company.official_email]
            subject = 'Confirmation mail'
            message = 'You will receive login credentials soon'
            send_mail(subject, message, sender_email, recipient_email)
            return JsonResponse({'success': True, 'message': 'Registration successful'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterUniversityInChargeView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': 'Invalid JSON'}, status=400)

        form = UniversityInChargeForm(data)
        if form.is_valid():
            university = form.save(commit=False)
            university.password = make_password(university.password)
            university.save()
            send_data_to_google_sheet3(
                university.university_name,
                university.official_email,
                university.country_code,
                university.mobile_number,
                university.password,
                university.linkedin_profile,
                university.college_person_name,
                university.agreed_to_terms,
                "Sheet3"
            )
            sender_email = settings.EMAIL_HOST_USER
            recipient_email = [university.official_email]
            subject = 'Confirmation mail'
            message = 'You will receive login credentials soon'
            send_mail(subject, message, sender_email, recipient_email)
            return JsonResponse({'success': True, 'message': 'Registration successful'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterConsultantView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': 'Invalid JSON'}, status=400)

        form = ConsultantForm(data)
        if form.is_valid():
            consultant = form.save(commit=False)
            consultant.password = make_password(consultant.password)
            consultant.save()
            send_data_to_google_sheet4(
                consultant.consultant_name,
                consultant.official_email,
                consultant.country_code,
                consultant.mobile_number,
                consultant.password,
                consultant.linkedin_profile,
                consultant.consultant_person_name,
                consultant.agreed_to_terms,
                "Sheet4"
            )
            sender_email = settings.EMAIL_HOST_USER
            recipient_email = [consultant.official_email]
            subject = 'Confirmation mail'
            message = 'You will receive login credentials soon'
            send_mail(subject, message, sender_email, recipient_email)
            return JsonResponse({'success': True, 'message': 'Registration successful'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors}, status=400)

@csrf_protect
def search(request):
    api_key = 'f120cebcf2a4379d72b80691ed4fe25bfc7443b11ce3739e6ee7e1bb790923505b48f76881878ee5f8f6af795bfc2c0be5c7d130dc820f3503bf58cced23e7c8462c10cf656a865164d8a6546f14a10f9c0bd31ed348f8774e6b47cb930a6266e13479cbf80f0a6e6c888e2c01696a0cd94b0b6d2da1dbc9eebc862985cdf64b'
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10)
    headers = {'Authorization': f'Bearer {api_key}'}

    apis = {
        'http://195.35.22.140:1337/api/abroad-exams': '/abroad-exam/{id}',
        'http://195.35.22.140:1337/api/bank-loans': '/bank-loan/{id}',
        'http://195.35.22.140:1337/api/do-and-donts': '/do-and-dont/{id}',
        'http://195.35.22.140:1337/api/exam-categories': '/exam-category/{id}',
        'http://195.35.22.140:1337/api/faqs': '/faq/{id}',
        'http://195.35.22.140:1337/api/general-instructions': '/general-instruction/{id}',
        'http://195.35.22.140:1337/api/instructions-and-navigations': '/instruction-and-navigation/{id}',
        'http://195.35.22.140:1337/api/practice-questions': '/practice-question/{id}',
        'http://195.35.22.140:1337/api/q-and-as': '/q-and-a/{id}',
        'http://195.35.22.140:1337/api/rules': '/rule/{id}',
        'http://195.35.22.140:1337/api/test-series-faqs': '/test-series-faq/{id}',
        'http://195.35.22.140:1337/api/college-infos?populate=*': '/college/{id}'
    }

    try:
        combined_result = []
        for api, path_template in apis.items():
            response = requests.get(api, headers=headers,timeout=9000)
            if response.status_code == 200:
                api_data = response.json().get('data', [])
                for item in api_data:
                    item['path'] = path_template.format(id=item['id'])
                    combined_result.append(item)

        matching_objects = [data for data in combined_result if query.lower() in json.dumps(data).lower()]
        paginator = Paginator(matching_objects, per_page)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        paginated_response = {
            'total_results': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': results.number,
            'results': results.object_list
        }

        return JsonResponse(paginated_response, safe=False)

    except requests.RequestException as e:
        return JsonResponse({'error': f'Error fetching API: {e}'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class Subscriber_view(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        form = SubscriptionForm(data)
        print(form.is_valid())
        if form.is_valid():
            subscriber=form.save()
            if subscriber.email and subscriber.subscribed_at:
                return JsonResponse({'message':f'you have successfully subscribed at {subscriber.subscribed_at}'})
            else:
                return JsonResponse({'error':'please subscribe'},status=400)
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class Subscriber_view1(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        form = SubscriptionForm1(data)
        print(form.is_valid())
        if form.is_valid():
            subscriber=form.save()
            if subscriber.email and subscriber.subscribed_at:
                return JsonResponse({'message':f'you have successfully subscribed at {subscriber.subscribed_at}'})
            else:
                return JsonResponse({'error':'please subscribe'},status=400)
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'errors': errors}, status=400)

csrf_exempt
def verify_token(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            token = body.get('token')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            userid = idinfo['sub']
            email = idinfo.get('email')
            name = idinfo.get('name')
            picture = idinfo.get('picture')

            users, created = User.objects.get_or_create(
                email=email,
                defaults={'google_id': userid, 'name': name, 'picture': picture}
            )

            if not created:
                users.name = name
                users.picture = picture
                users.save()

            return JsonResponse({'message': 'Token is valid', 'user': {
                'email': User.email,
                'name': User.name,
                'picture': User.picture,
            }}, status=200)
        except ValueError:

            return JsonResponse({'error': 'Invalid token'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


