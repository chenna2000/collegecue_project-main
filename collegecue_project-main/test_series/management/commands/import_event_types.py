import pandas as pd  # type: ignore
from django.core.management.base import BaseCommand
from test_series.models import Exam, ProctoringEvent, ProctoringSession, Question
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Import event types and question data from Excel files to the ProctoringEvent and Question models'

    def add_arguments(self, parser):
        parser.add_argument('--event_type', type=str, help='Path to the Excel file containing event types')
        parser.add_argument('--question_status', type=str, help='Path to the Excel file containing question statuses')
        parser.add_argument('--question_section_type', type=str, help='Path to the Excel file containing question section types')
        parser.add_argument('--session_status_type', type=str, help='Path to the Excel file containing session statuses')
        parser.add_argument('--session_id', type=int, required=True, help='Session ID to associate with ProctoringEvent')
        parser.add_argument('--exam_id', type=int, required=True, help='Exam ID to associate with Questions')
        parser.add_argument('--user_id', type=int, required=True, help='User ID to associate with ProctoringSession')

    def handle(self, *args, **kwargs):
        event_type_path = kwargs['event_type']
        question_status_path = kwargs['question_status']
        question_section_type_path = kwargs['question_section_type']
        session_status_type_path = kwargs['session_status_type']
        session_id = kwargs['session_id']
        exam_id = kwargs['exam_id']
        user_id = kwargs['user_id']

        try:
            session = ProctoringSession.objects.get(id=session_id)
        except ProctoringSession.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No session found with ID {session_id}'))
            return

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No user found with ID {user_id}'))
            return

        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No exam found with ID {exam_id}'))
            return

        try:
            event_type_df = pd.read_excel(event_type_path)
            question_status_df = pd.read_excel(question_status_path)
            question_section_df = pd.read_excel(question_section_type_path)
            session_status_df = pd.read_excel(session_status_type_path)

            max_rows = max(
               len(event_type_df),
               len(question_status_df),
               len(question_section_df),
               len(session_status_df),
            )

            next_question_no = Question.objects.filter(exam=exam).count() + 1

            for i in range(max_rows):
                event_type = event_type_df.iloc[i]['event_type'] if i < len(event_type_df) else None
                question_status = question_status_df.iloc[i]['status'] if i < len(question_status_df) else None
                question_section_type = question_section_df.iloc[i]['section'] if i < len(question_section_df) else None
                session_status_type = session_status_df.iloc[i]['session_status'] if i < len(session_status_df) else None

                if event_type:
                    ProctoringEvent.objects.get_or_create(
                        event_type=event_type,
                        session=session,
                    )

                if question_status or question_section_type:
                    Question.objects.create(
                        exam=exam,
                        question_no=next_question_no,
                        section=question_section_type if question_section_type else '',
                        status=question_status if question_status else ''
                    )
                    next_question_no += 1

                if session_status_type:
                    ProctoringSession.objects.create(
                      status=session_status_type,
                      user=user,
                      exam=exam
                    )

            self.stdout.write(self.style.SUCCESS('Data import and update completed successfully.'))

        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'File not found: {e.filename}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading Excel file: {str(e)}'))

