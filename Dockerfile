FROM praekeltfoundation/django-bootstrap:py3.6

COPY setup.py /app
RUN pip install --no-cache-dir -e .
ENV DJANGO_SETTINGS_MODULE "config.settings.production"

COPY . /app
RUN GOOGLE_PLACES_API_KEY=placeholder SECRET_KEY=placeholder ALLOWED_HOSTS=placeholder python manage.py collectstatic --noinput
CMD ["config.wsgi:application"]
