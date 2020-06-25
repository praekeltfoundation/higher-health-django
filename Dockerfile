FROM praekeltfoundation/django-bootstrap:py3.6

COPY setup.py /app
RUN pip install --no-cache-dir -e .
ENV DJANGO_SETTINGS_MODULE "config.settings.production"

COPY . /app
RUN CELERY_BROKER_URL=amqp:// EVENTSTORE_URL=placeholder EVENTSTORE_TOKEN=placeholder GOOGLE_PLACES_CLIENT_API_KEY=placeholder GOOGLE_PLACES_SERVER_API_KEY=placeholder GOOGLE_GA_TAG_KEY=placeholder SECRET_KEY=placeholder ALLOWED_HOSTS=placeholder python manage.py collectstatic --noinput
CMD ["config.wsgi:application"]
