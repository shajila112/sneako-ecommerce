import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sneako_project.settings')
django.setup()

try:
    print("Running makemigrations...")
    call_command('makemigrations', 'adminpanel')
    print("Running migrate...")
    call_command('migrate', 'adminpanel')
    print("Migrations applied successfully!")
except Exception as e:
    print(f"Error: {e}")
