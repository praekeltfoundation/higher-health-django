from django.conf import settings


def api_keys(request):
    return {"PLACES_API_KEY": settings.CLIENT_PLACES_API_KEY}

def ga_tags(request):
    return {"GA_TAG": settings.GA_TAG_KEY}
