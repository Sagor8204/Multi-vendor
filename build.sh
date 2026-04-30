#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate


# create for superuser
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); import django; django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); not User.objects.filter(username='admin').exists() and User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')"

# my seed_db command will be create couple of fake data
python manage.py seed_db