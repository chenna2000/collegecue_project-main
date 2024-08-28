from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('proctoring/start/', views.start_proctoring_session, name='start_proctoring_session'),
    path('proctoring/end/', views.end_proctoring_session, name='end_proctoring_session'),
    path('proctoring/event/', views.record_proctoring_event, name='record_proctoring_event'),
    path('count-questions/<int:exam_id>/', views.count_questions, name='count_questions'),
    path('event-types/', views.fetch_event_types, name='event-types'),
    path('section-types/', views.fetch_section_types, name='section-types'),
    path('status-types/', views.fetch_status_types, name='status-types'),
    path('session-status-types/', views.fetch_session_status, name='session-status-types'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('mark-for-review/', views.mark_for_review, name='mark_for_review'),
    path('session-status/<int:session_id>/', views.get_session_status, name='get_session_status'),
    path('question/<int:session_id>/<int:question_no>/', views.get_question_details, name='get_question_details'),
    path('user-score/<int:exam_id>/', views.get_user_score, name='get_user_score'),
    path('get-details/', views.get_details, name='get_details'),
    path('submit-all-answers/', views.submit_all_answers, name='submit_all_answers'),
    path('question/next/<int:session_id>/<int:current_question_no>/', views.get_next_question, name='get_next_question'),
    path('question/previous/<int:session_id>/<int:current_question_no>/', views.get_previous_question, name='get_previous_question'),
    path('submit-details/', views.submit_details, name='submit_details'),
]
