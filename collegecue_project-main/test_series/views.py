import json
from django.shortcuts import get_object_or_404 # type: ignore
from django.http import JsonResponse # type: ignore
from django.utils import timezone # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from django.views.decorators.http import require_POST, require_GET # type: ignore
from .models import ProctoringEvent, ProctoringSession, Exam, Question, UserResponse, UserScore
from .forms import ExamParticipantForm, MarkForReviewForm, StartProctoringSessionForm, EndProctoringSessionForm, RecordProctoringEventForm, SubmitAllAnswersForm, SubmitAnswerForm
from django.contrib.auth import authenticate, login as auth_login # type: ignore
from django.core.mail import send_mail # type: ignore
from django.conf import settings # type: ignore

def api_response(success, data=None, error=None, details=None, status=200):
    response = {'success': success}
    if data:
        response['data'] = data
    if error:
        response['error'] = error
    if details:
        response['details'] = details
    return JsonResponse(response, status=status)

@csrf_exempt
@require_POST
def custom_login(request):
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return api_response(success=True, data={'message': 'Login successful'})
        else:
            return api_response(success=False, error='Invalid credentials', status=400)
    except Exception as e:
        return api_response(success=False,  error='An error occurred during login', details =str(e), status=500)

@login_required
@require_POST
@csrf_exempt
def start_proctoring_session(request):
    try:
        form = StartProctoringSessionForm(request.POST)
        if form.is_valid():
            exam_id = form.cleaned_data['exam_id']
            exam = get_object_or_404(Exam, id=exam_id)

            if ProctoringSession.objects.filter(user=request.user, exam=exam).exists():
                return api_response(success=False, error='Proctoring session for this exam already exists', status=400)

            session = ProctoringSession.objects.create(
                user=request.user,
                exam=exam,
                start_time=timezone.now(),
                status='ongoing'
            )

            user_email = request.user.email
            try:
                send_mail(
                    "Proctoring Event Notification",
                    "Session started",
                    settings.EMAIL_HOST_USER,
                    [user_email]
                )
            except Exception as email_error:
                return api_response(success=True, data={'session_id': session.id}, error='Failed to send email notification', details=str(email_error),status=500)

            return api_response(success=True, data={'session_id': session.id})
        else:
            return api_response(success=False, error='Invalid data', status=400)
    except Exception as e:
        return api_response(success=False, error='An error occurred while starting the session', details =str(e), status=500)

@login_required
@require_POST
@csrf_exempt
def end_proctoring_session(request):
    try:
        form = EndProctoringSessionForm(request.POST)
        if form.is_valid():
            session_id = form.cleaned_data['session_id']
            session = get_object_or_404(ProctoringSession, id=session_id)
            session.end_time = timezone.now()
            session.status = 'completed'
            session.save()

            user_email = request.user.email
            try:
                send_mail(
                    "Proctoring Event Notification",
                    "Session ended",
                    settings.EMAIL_HOST_USER,
                    [user_email]
                )
            except Exception as email_error:
                return api_response(success=True, data={'status': 'completed'}, error=f'Failed to send email to {user_email}',details = str(email_error) ,status=500)

            return api_response(success=True, data={'status': 'completed'})
        else:
            return api_response(success=False, error='Invalid data', status=400)
    except Exception as e:
        return api_response(success=False, error='An error occurred while ending the session', details =str(e),status=500)

@login_required
@require_POST
@csrf_exempt
def record_proctoring_event(request):
    try:
        form = RecordProctoringEventForm(request.POST)
        if form.is_valid():
            session_id = form.cleaned_data['session_id']
            session = get_object_or_404(ProctoringSession, id=session_id)

            if ProctoringEvent.objects.filter(session=session).exists():
                return api_response(success=False, error='Event for this session already recorded', status=400)

            event = form.save(commit=False)
            event.session = session
            event.save()

            user_email = request.user.email
            try:
                send_mail(
                    "Proctoring Event Notification",
                    "Event recorded",
                    settings.EMAIL_HOST_USER,
                    [user_email]
                )
            except Exception as email_error:
                return api_response(success=True, data={'status': 'event recorded'}, error='Failed to send email notification', details =str(email_error), status=500)

            return api_response(success=True, data={'status': 'event recorded'})
        else:
            return api_response(success=False, error='Invalid data', status=400)
    except Exception as e:
        return api_response(success=False, error='An error occurred while recording the event', details =str(e), status=500)

# @login_required
# @require_POST
# @csrf_exempt
# def submit_answer(request):
#     try:
#         form = SubmitAnswerForm(request.POST)
#         if form.is_valid():
#             session_id = form.cleaned_data['session_id']
#             session = get_object_or_404(ProctoringSession, id=session_id)
#             question_no = form.cleaned_data['question_no']
#             selected_option = form.cleaned_data['selected_option']

#             question = get_object_or_404(Question, exam=session.exam, question_no=question_no)

#             if question.status != 'Answered':
#                 question.status = 'Answered'
#                 question.save()

#             if UserResponse.objects.filter(user=request.user, question=question, session=session).exists():
#                 return api_response(success=False, error='Answer already submitted', status=400)

#             UserResponse.objects.create(
#                 user=request.user,
#                 question=question,
#                 session=session,
#                 selected_option=selected_option,
#                 response_time=timezone.now()
#             )

#             if selected_option == question.correct_option:
#                 user_score ,created= UserScore.objects.get_or_create(user=request.user, exam=session.exam)
#                 user_score.score += 1
#                 user_score.save()

#             return api_response(success=True, data={'message': 'Answer submitted successfully'})
#         else:
#             return api_response(success=False, error='Invalid data', status=400)
#     except Exception as e:
#         return api_response(success=False, error='An error occurred while submitting the answer', details =str(e), status=500)

@login_required
@require_POST
@csrf_exempt
def submit_answer(request):
    try:
        form = SubmitAnswerForm(request.POST)
        if form.is_valid():
            session_id = form.cleaned_data['session_id']
            session = get_object_or_404(ProctoringSession, id=session_id)
            question_no = form.cleaned_data['question_no']
            selected_option = form.cleaned_data['selected_option']

            question = get_object_or_404(Question, exam=session.exam, question_no=question_no)

            if question.status != 'Answered':
                question.status = 'Answered'
                question.save()

            if UserResponse.objects.filter(user=request.user, question=question, session=session).exists():
                return api_response(success=False, error='Answer already submitted', status=400)

            UserResponse.objects.create(
                user=request.user,
                question=question,
                session=session,
                selected_option=selected_option,
                response_time=timezone.now()
            )

            if selected_option == question.correct_option:
                user_score = UserScore.objects.get_or_create(user=request.user, exam=session.exam)[0]
                user_score.score += 1
                user_score.save()

            return api_response(success=True, data={'message': 'Answer submitted successfully'})
        else:
            return api_response(success=False, error='Invalid data', status=400)
    except Exception as e:
        return api_response(success=False, error='An error occurred while submitting the answer', details=str(e), status=500)

@login_required
def get_session_status(request, session_id):
    try:
        session = get_object_or_404(ProctoringSession, id=session_id)

        total_questions = session.exam.questions.count()
        print(total_questions)

        answered_questions = session.exam.questions.filter(status="Answered").count()
        not_answered_questions = session.exam.questions.filter(status="Not Answered").count()
        not_visited_questions = session.exam.questions.filter(status="Not Visited").count()
        marked_for_review = session.exam.questions.filter(status="Mark for Review").count()

        remaining_time = session.duration - (timezone.now() - session.start_time)

        status = {
            'answered_questions': answered_questions,
            'not_answered_questions': not_answered_questions,
            'marked_for_review': marked_for_review,
            'not_visited_questions': not_visited_questions,
            'remaining_time': remaining_time.total_seconds(),
            'total_questions': total_questions,
        }

        return JsonResponse(status, status=200)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred while fetching session status', 'details': str(e)}, status=500)


@login_required
@require_GET
def get_question_details(request, session_id, question_no):
    try:
        session = get_object_or_404(ProctoringSession, id=session_id)
        question = get_object_or_404(Question, exam=session.exam, question_no=question_no)
        response_data = {
            'question_no': question.question_no,
            'question_text': question.question_text,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4,
            'status': question.status,
            'section': question.section,
        }
        return api_response(success=True, data=response_data)
    except Exception as e:
        return api_response(success=False, error='An error occurred while fetching the question details', details =str(e), status=500)


def count_questions(request, exam_id):
    try:
        exam = Exam.objects.filter(id=exam_id).first()
        if not exam:
            return api_response(success=False, error='Exam ID not found', status=404)

        question_count = Question.objects.filter(exam_id=exam_id).count()

        if question_count == 0:
            return api_response(success=False, error='No Questions found for this Exam', data={'exam_name': exam.name}, status=404)
        else:
            return api_response(success=True, data={'question_count': question_count, 'exam_name': exam.name})
    except Exception as e:
        return api_response(success=False, error='An error occurred while counting questions', details =str(e), status=500)

@csrf_exempt
@login_required
@require_POST
def mark_for_review(request):
    try:
        form = MarkForReviewForm(json.loads(request.body))
        if form.is_valid():
            session_id = form.cleaned_data['session_id']
            question_no = form.cleaned_data['question_no']
            mark = form.cleaned_data['mark']
            session = get_object_or_404(ProctoringSession, id=session_id)
            question = get_object_or_404(Question, exam=session.exam, question_no=question_no)

            question.status = 'Mark for Review' if mark else 'Not Answered'
            question.save()

            return api_response(success=True, data={'status': 'Question marked for review' if mark else 'Mark for review removed'})
        else:
            return api_response(success=False, error='Invalid data', status=400)
    except Exception as e:
        return api_response(success=False, error='An error occurred while marking the question for review', details =str(e), status=500)

def fetch_event_types(request):
    if request.method == 'GET':
        events = ProctoringEvent.objects.all()

        event_types = {
            event.event_type: event.event_type
            for event in events
            if event.event_type
        }
        return JsonResponse({'event_types': event_types})

def fetch_section_types(request):
    if request.method == 'GET':
        questions = Question.objects.all()

        section_types = {
            question.section: question.section
            for question in questions
            if question.section
        }
        return JsonResponse({'section_types': section_types})

def fetch_status_types(request):
    if request.method == 'GET':
        questions = Question.objects.all()

        status_types = {
            question.status: question.status
            for question in questions
            if question.status
        }
        return JsonResponse({'status_types': status_types})

def fetch_session_status(request):
    if request.method == 'GET':
        sessions = ProctoringSession.objects.all()

        session_status_types ={
            session.status: session.status
            for session in sessions
            if session.status
        }
        return JsonResponse({'session_status_types': session_status_types})

def fetch_user_score(user, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        user_score = get_object_or_404(UserScore, user=user, exam=exam)
        return user_score.score

@login_required
@require_GET
def get_user_score(request, exam_id):
    try:
        user = request.user
        score = fetch_user_score(user, exam_id)

        response_data = {
            'user': user.username,
            'exam': Exam.objects.get(id=exam_id).name,
            'score': score
        }
        return api_response(success=True, data=response_data)
    except Exception as e:
        return api_response(success=False, error='An error occurred while fetching user score', details=str(e), status=500)

@csrf_exempt
def get_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')

            session = get_object_or_404(ProctoringSession, id=session_id)
            exam = session.exam
            exam_id = exam.id

            score = fetch_user_score(request.user, exam_id)

            answered_questions = exam.questions.filter(status="Answered").count()
            not_answered_questions = exam.questions.filter(status="Not Answered").count()
            not_visited_questions = exam.questions.filter(status="Not Visited").count()
            marked_for_review = exam.questions.filter(status="Mark for Review").count()

            details = {
                'Name': data.get('name'),
                'Phone': data.get('mobile_no'),
                'Email': data.get('email'),
                'Score': score,  
                'answered_questions': answered_questions,
                'not_answered_questions': not_answered_questions,
                'marked_for_review': marked_for_review,
                'not_visited_questions': not_visited_questions,
            }

            return JsonResponse({'Quiz Summary': details}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred', 'details': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# @csrf_exempt
# @require_POST
# def submit_all_answers(request):
#     try:
#         form = SubmitAllAnswersForm(json.loads(request.body))
#         if form.is_valid():
#             session_id = form.cleaned_data['session_id']
#             answers = form.cleaned_data['answers']

#             session = get_object_or_404(ProctoringSession, id=session_id)

#             for answer in answers:
#                 question_no = answer['question_no']
#                 selected_option = answer['selected_option']

#                 question = get_object_or_404(Question, exam=session.exam, question_no=question_no)

#                 existing_response = UserResponse.objects.filter(
#                     user=request.user,
#                     question=question,
#                     session=session
#                 ).first()

#                 if existing_response:
#                     existing_response.selected_option = selected_option
#                     existing_response.response_time = timezone.now()
#                     existing_response.save()
#                 else:
#                     UserResponse.objects.create(
#                         user=request.user,
#                         question=question,
#                         session=session,
#                         selected_option=selected_option,
#                         response_time=timezone.now()
#                     )
#                     if selected_option == question.correct_option:
#                         user_score, created = UserScore.objects.get_or_create(user=request.user, exam=session.exam)
#                         user_score.score += 1
#                         user_score.save()

#                 question.status = 'Answered'
#                 question.save()

#             return JsonResponse({'success': True, 'message': 'Go to details page'}, status=200)
#         else:
#             return JsonResponse({'success': False, 'error': 'Invalid data', 'details': form.errors}, status=400)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': 'An error occurred while submitting all answers', 'details': str(e)}, status=500)

@csrf_exempt
@require_POST
def submit_all_answers(request):
    try:
        form = SubmitAllAnswersForm(json.loads(request.body))
        if form.is_valid():
            session_id = form.cleaned_data['session_id']
            answers = form.cleaned_data['answers']

            session = get_object_or_404(ProctoringSession, id=session_id)

            for answer in answers:
                question_no = answer['question_no']
                selected_option = answer['selected_option']

                question = get_object_or_404(Question, exam=session.exam, question_no=question_no)

                existing_response = UserResponse.objects.filter(
                    user=request.user,
                    question=question,
                    session=session
                ).first()

                if existing_response:
                    existing_response.selected_option = selected_option
                    existing_response.response_time = timezone.now()
                    existing_response.save()
                else:
                    UserResponse.objects.create(
                        user=request.user,
                        question=question,
                        session=session,
                        selected_option=selected_option,
                        response_time=timezone.now()
                    )
                    if selected_option == question.correct_option:
                        user_score = UserScore.objects.get_or_create(user=request.user, exam=session.exam)[0]
                        user_score.score += 1
                        user_score.save()

                question.status = 'Answered'
                question.save()

            return JsonResponse({'success': True, 'message': 'Go to details page'}, status=200)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid data', 'details': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred while submitting all answers', 'details': str(e)}, status=500)


@login_required
@require_GET
def get_next_question(request, session_id, current_question_no):
    try:
        session = get_object_or_404(ProctoringSession, id=session_id)
        exam = session.exam
        next_question = Question.objects.filter(exam=exam, question_no__gt=current_question_no).order_by('question_no').first()

        if not next_question:
            return JsonResponse({'success': False, 'error': 'No next question available'}, status=404)

        response_data = {
            'question_no': next_question.question_no,
            'question_text': next_question.question_text,
            'option1': next_question.option1,
            'option2': next_question.option2,
            'option3': next_question.option3,
            'option4': next_question.option4,
            'status': next_question.status,
            'section': next_question.section,
        }
        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred while fetching the next question', 'details': str(e)}, status=500)

@login_required
@require_GET
def get_previous_question(request, session_id, current_question_no):
    try:
        session = get_object_or_404(ProctoringSession, id=session_id)
        exam = session.exam
        previous_question = Question.objects.filter(exam=exam, question_no__lt=current_question_no).order_by('-question_no').first()

        if not previous_question:
            return JsonResponse({'success': False, 'error': 'No previous question available'}, status=404)

        response_data = {
            'question_no': previous_question.question_no,
            'question_text': previous_question.question_text,
            'option1': previous_question.option1,
            'option2': previous_question.option2,
            'option3': previous_question.option3,
            'option4': previous_question.option4,
            'status': previous_question.status,
            'section': previous_question.section,
        }
        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred while fetching the previous question', 'details': str(e)}, status=500)

@csrf_exempt
def submit_details(request):
    if request.method == 'POST':
        form = ExamParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.exam_started = True
            participant.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Exam details submitted successfully',
                'participant_id': participant.id,
                'exam_started': participant.exam_started
            })
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })