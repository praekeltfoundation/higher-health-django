from django.conf import settings


def api_keys(request):
    return {"PLACES_API_KEY": settings.CLIENT_PLACES_API_KEY}


def ga_tags(request):
    return {"GA_TAGS": settings.GA_TAG_KEYS}

def sentry_connect(request):
    return {"SENTRY_DSN": settings.SENTRY_SDSN}
