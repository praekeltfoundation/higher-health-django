import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa
from .base import env

DEBUG = False

# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env.str("SECRET_KEY")

ALLOWED_HOSTS = env.str("ALLOWED_HOSTS").split(",")

# Configure Sentry Logging
SENTRY_DSN = env.str("SENTRY_DSN", "")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN, integrations=[DjangoIntegration()], send_default_pii=True
    )

CLIENT_PLACES_API_KEY = env.str("GOOGLE_PLACES_CLIENT_API_KEY")
SERVER_PLACES_API_KEY = env.str("GOOGLE_PLACES_SERVER_API_KEY")

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
