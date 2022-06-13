from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.shortcuts import redirect, reverse


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        maintenance = getattr(settings, 'MAINTENANCE_MODE', None)
        # This should cause the middleware to be removed from the pipeline
        # if we're not in maintenance mode
        if not maintenance:
            raise MiddlewareNotUsed


    def __call__(self, request):
        maintenance = getattr(settings, 'MAINTENANCE_MODE', None)
        if maintenance and reverse('healthcheck_maintenance') not in request.path:
            response = redirect(reverse("healthcheck_maintenance"))
            return response
        response = self.get_response(request)

        return response
