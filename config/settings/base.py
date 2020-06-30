"""
Django settings for higher_health_django project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

import os
from os.path import join

import environ

root = environ.Path(__file__) - 3
env = environ.Env(DEBUG=(bool, False))

ROOT_DIR = root()


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = root()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "4jt$o42*aafm&9lr5fb5=rw$)2$=o42eaa2(a%o5*)o9ly=q!m"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "higher_health",
    "import_export",
    "compressor",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "higher_health.context_processors.api_keys",
                "higher_health.context_processors.ga_tags",
                "higher_health.context_processors.sentry_connect",
            ]
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": env.db(
        "HIGHER_HEALTH_DATABASE",
        default="postgres://postgres@localhost:5432/higher_health",
    )
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/login/"


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Johannesburg"

USE_I18N = True

USE_L10N = True

USE_TZ = True


GA_TAG_KEYS = env.list("GOOGLE_GA_TAG_KEYS", default=[])
SENTRY_DSN = env.str("SENTRY_DSN", "REPLACE_ME")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        send_default_pii=True,
    )
CLIENT_PLACES_API_KEY = env.str("GOOGLE_PLACES_CLIENT_API_KEY", "REPLACE_ME")
SERVER_PLACES_API_KEY = env.str("GOOGLE_PLACES_SERVER_API_KEY", "REPLACE_ME")

RAPIDPRO_TOKEN = env.str("RAPIDPRO_TOKEN", "REPLACE_ME")
RAPIDPRO_URL = env.str("RAPIDPRO_URL", "REPLACE_ME")
RAPIDPRO_SEND_OTP_SMS_FLOW = env.str("RAPIDPRO_SEND_OTP_SMS_FLOW", "REPLACE_ME")

OTP_EXPIRES_DURATION = env.int("OTP_EXPIRES_DURATION", 60 * 5)
OTP_BACKOFF_DURATION = env.int("OTP_BACKOFF_DURATION", 60 * 15)
OTP_RETRIES_LIMIT = env.int("OTP_RETRIES_LIMIT", 3)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "compressor.finders.CompressorFinder",
)


STATIC_ROOT = join(ROOT_DIR, "static")
STATIC_URL = "/static/"
COMPRESS_ENABLED = True

CACHES = {"default": env.cache("CACHE_URL", default="locmemcache://")}

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "amqp://")

EVENTSTORE_URL = env.str("EVENTSTORE_URL", "https://eventstore-placeholder")
EVENTSTORE_TOKEN = env.str("EVENTSTORE_TOKEN", "placeholder-token")
