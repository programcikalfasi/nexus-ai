web: gunicorn nexus_ai.wsgi --bind 0.0.0.0:$PORT
release: python manage.py migrate && python manage.py collectstatic --no-input
