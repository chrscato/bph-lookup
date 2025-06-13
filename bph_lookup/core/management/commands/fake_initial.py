# Save this as: bph_lookup/core/management/commands/fake_initial.py

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os

class Command(BaseCommand):
    help = 'Sets up Django to work with existing compensation_rates.db'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset migrations even if they exist',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Django with existing database...'))

        # Check if database file exists
        db_path = 'compensation_rates.db'
        if not os.path.exists(db_path):
            self.stdout.write(
                self.style.ERROR(f'Database file {db_path} not found!')
            )
            return

        # Step 1: Delete existing migrations if force is specified
        if options['force']:
            self.stdout.write('Removing existing migrations...')
            migrations_dir = 'core/migrations'
            if os.path.exists(migrations_dir):
                for file in os.listdir(migrations_dir):
                    if file.endswith('.py') and file != '__init__.py':
                        os.remove(os.path.join(migrations_dir, file))
                        self.stdout.write(f'Removed {file}')

        # Step 2: Check what tables exist in the database
        self.stdout.write('Checking existing database tables...')
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
        # Print existing tables
        self.stdout.write('Existing tables:')
        for table in sorted(existing_tables):
            if not table.startswith('django_') and not table.startswith('auth_'):
                self.stdout.write(f'  - {table}')

        # Step 3: Create initial migration
        self.stdout.write('\nCreating initial migration...')
        try:
            call_command('makemigrations', 'core', verbosity=2)
            self.stdout.write(self.style.SUCCESS('Initial migration created'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating migration: {e}'))
            return

        # Step 4: Fake apply the initial migration
        self.stdout.write('Fake applying initial migration...')
        try:
            call_command('migrate', 'core', '--fake-initial', verbosity=2)
            self.stdout.write(self.style.SUCCESS('Initial migration fake applied'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fake applying migration: {e}'))
            return

        # Step 5: Apply other Django migrations
        self.stdout.write('Applying other Django migrations...')
        try:
            call_command('migrate', verbosity=2)
            self.stdout.write(self.style.SUCCESS('All migrations applied'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Some migrations may have failed: {e}'))

        # Step 6: Test database connection
        self.stdout.write('\nTesting database queries...')
        try:
            from core.models import State, ProcedureCode, CmsRvu
            
            state_count = len([table for table in existing_tables if table == 'state'])
            if state_count:
                try:
                    states = State.objects.count()
                    self.stdout.write(f'  - States table: {states} records')
                except Exception as e:
                    self.stdout.write(f'  - States table: Error ({e})')
            
            proc_count = len([table for table in existing_tables if table == 'procedure_code'])
            if proc_count:
                try:
                    procedures = ProcedureCode.objects.count()
                    self.stdout.write(f'  - Procedure codes: {procedures} records')
                except Exception as e:
                    self.stdout.write(f'  - Procedure codes: Error ({e})')
            
            rvu_count = len([table for table in existing_tables if table == 'cms_rvu'])
            if rvu_count:
                try:
                    rvus = CmsRvu.objects.count()
                    self.stdout.write(f'  - CMS RVUs: {rvus} records')
                except Exception as e:
                    self.stdout.write(f'  - CMS RVUs: Error ({e})')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error testing queries: {e}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Setup completed!'))
        self.stdout.write('Next steps:')
        self.stdout.write('1. Test your application with: python manage.py runserver')
        self.stdout.write('2. Create a superuser with: python manage.py createsuperuser')
        self.stdout.write('3. Check admin interface to verify data access')