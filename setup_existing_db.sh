#!/bin/bash

# Setup script for existing compensation_rates.db

echo "🔧 Setting up Django with existing database..."

# Check if compensation_rates.db exists
if [ ! -f "compensation_rates.db" ]; then
    echo "❌ Error: compensation_rates.db file not found!"
    echo "Please make sure the database file is in the project root directory."
    exit 1
fi

echo "✅ Database file found"

# Backup existing migrations if they exist
if [ -d "bph_lookup/core/migrations" ]; then
    echo "📦 Backing up existing migrations..."
    mv bph_lookup/core/migrations bph_lookup/core/migrations_backup_$(date +%Y%m%d_%H%M%S)
fi

# Create fresh migrations directory
mkdir -p bph_lookup/core/migrations
echo "# Django migrations" > bph_lookup/core/migrations/__init__.py

# Go to Django project directory
cd bph_lookup

echo "🐍 Activating virtual environment and installing dependencies..."
if [ ! -d "../venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ../venv
fi

source ../venv/bin/activate
pip install -r ../requirements.txt

echo "📊 Checking database structure..."
python manage.py check_db

echo "📝 Creating initial migration..."
python manage.py makemigrations core

echo "🔄 Fake applying initial migration..."
python manage.py migrate core --fake-initial

echo "🚀 Applying remaining Django migrations..."
python manage.py migrate

echo "🔍 Testing database connection..."
python manage.py shell -c "
from core.models import *
print('Testing model access...')
try:
    print(f'CMS RVU records: {CmsRvu.objects.count()}')
    print(f'CMS GPCI records: {CmsGpci.objects.count()}')
    print(f'Medicare Locality Map records: {MedicareLocalityMap.objects.count()}')
    print('✅ Database models working correctly!')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo "📋 Collecting static files..."
python manage.py collectstatic --noinput

echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Create a superuser: python manage.py createsuperuser"
echo "2. Test the application: python manage.py runserver"
echo "3. Visit http://localhost:8000 to test the lookup functionality"
echo "4. Visit http://localhost:8000/admin to check the admin interface"