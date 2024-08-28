import pandas as pd # type: ignore
from django.core.management.base import BaseCommand
from job_portal.models import Application, Job, Company

class Command(BaseCommand):
    help = 'Import data from multiple Excel files to the Job, Company, and Application models'

    def add_arguments(self, parser):
        parser.add_argument('job_title', type=str, help='Path to the Excel file containing job titles')
        parser.add_argument('job_type', type=str, help='Path to the Excel file containing job types')
        parser.add_argument('exp_type', type=str, help='Path to the Excel file containing job experience')
        parser.add_argument('category_type', type=str, help='Path to the Excel file containing job categories')
        parser.add_argument('workplace_types', type=str, help='Path to the Excel file containing workplace types')
        parser.add_argument('location_types', type=str, help='Path to the Excel file containing job locations')
        parser.add_argument('sector_type', type=str, help='Path to the Excel file containing sector types')
        parser.add_argument('country_type', type=str, help='Path to the Excel file containing country names')
        parser.add_argument('application_status', type=str, help='Path to the Excel file containing application statuses')

    def handle(self, *args, **kwargs):
        job_titles_path = kwargs['job_title']
        job_types_path = kwargs['job_type']
        experience_path = kwargs['exp_type']
        categories_path = kwargs['category_type']
        workplace_types_path = kwargs['workplace_types']
        locations_path = kwargs['location_types']
        sector_types_path = kwargs['sector_type']
        country_names_path = kwargs['country_type']
        statuses_path = kwargs['application_status']

        try:
            job_titles_df = pd.read_excel(job_titles_path)
            job_types_df = pd.read_excel(job_types_path)
            experience_df = pd.read_excel(experience_path)
            categories_df = pd.read_excel(categories_path)
            workplace_types_df = pd.read_excel(workplace_types_path)
            locations_df = pd.read_excel(locations_path)
            sector_types_df = pd.read_excel(sector_types_path)
            country_names_df = pd.read_excel(country_names_path)
            statuses_df = pd.read_excel(statuses_path)

            max_rows = max(
                len(job_titles_df),
                len(job_types_df),
                len(experience_df),
                len(categories_df),
                len(workplace_types_df),
                len(locations_df),
                len(sector_types_df),
                len(country_names_df),
                len(statuses_df)
            )

            for i in range(max_rows):
                job_title = job_titles_df.iloc[i]['job_title'] if i < len(job_titles_df) else ''
                job_type = job_types_df.iloc[i]['job_type'] if i < len(job_types_df) else ''
                experience = experience_df.iloc[i]['experience'] if i < len(experience_df) else ''
                category = categories_df.iloc[i]['category'] if i < len(categories_df) else ''
                workplace_type = workplace_types_df.iloc[i]['workplaceTypes'] if i < len(workplace_types_df) else ''
                location = locations_df.iloc[i]['location'] if i < len(locations_df) else ''
                sector_type = sector_types_df.iloc[i]['sector_type'] if i < len(sector_types_df) else ''
                country_name = country_names_df.iloc[i]['country_name'] if i < len(country_names_df) else ''
                status = statuses_df.iloc[i]['status'] if i < len(statuses_df) else ''

                if sector_type or country_name:
                    Company.objects.get_or_create(
                        sector_type=sector_type,
                        country_name=country_name
                    )

                if job_title or job_type or experience or category or workplace_type or location:
                    job, _= Job.objects.get_or_create(
                        job_title=job_title,
                        job_type=job_type,
                        experience=experience,
                        category=category,
                        workplaceTypes=workplace_type,
                        location=location,
                    )

                if job and status:
                    Application.objects.create(
                        job=job,
                        status=status,
                    )

                self.stdout.write(self.style.SUCCESS(f'Successfully imported Application row {i+1}'))

        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'File not found: {e.filename}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))

