from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "TESTSEKRET"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

ENV_HOSTS = [host for host in env.str("ALLOWED_HOSTS", "").split(",") if host]
ALLOWED_HOSTS = ENV_HOSTS + ["localhost", ".localhost", "127.0.0.1", "0.0.0.0"]

CLIENT_PLACES_API_KEY = "TEST_API_KEY"
SERVER_PLACES_API_KEY = "TEST_API_KEY"

RAPIDPRO_TOKEN = None
RAPIDPRO_URL = None
RAPIDPRO_SEND_OTP_SMS_FLOW = None

CELERY_TASK_ALWAYS_EAGER = True
