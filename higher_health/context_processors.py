from django.conf import settings


def api_keys(request):
    return {"PLACES_API_KEY": settings.CLIENT_PLACES_API_KEY}
