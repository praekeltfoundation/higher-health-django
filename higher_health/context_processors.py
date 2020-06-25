from django.conf import settings


def api_keys(request):
    return {"PLACES_API_KEY": settings.CLIENT_PLACES_API_KEY}


def ga_tags(request):
    if settings.GA_TAG_KEYS:
        split_keys = [x.strip() for x in settings.GA_TAG_KEYS.split(",")]
        return {"GA_TAGS": split_keys}
