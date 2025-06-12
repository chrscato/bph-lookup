from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Count
from core.models import (
    MedicareLocalityMap,
    MedicareLocalityMeta,
    CmsGpci,
    CmsRvu,
    CmsConversionFactor
)

class Command(BaseCommand):
    help = 'Verifies database connection and shows row counts for each table'

    def handle(self, *args, **options):
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('Database connection successful!'))
            
            # Get counts for each model
            models = [
                MedicareLocalityMap,
                MedicareLocalityMeta,
                CmsGpci,
                CmsRvu,
                CmsConversionFactor
            ]
            
            self.stdout.write('\nTable Row Counts:')
            self.stdout.write('-' * 30)
            
            for model in models:
                count = model.objects.count()
                self.stdout.write(f'{model._meta.db_table}: {count:,} rows')
            
            self.stdout.write(self.style.SUCCESS('\nDatabase check completed successfully!'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking database: {str(e)}')
            ) 