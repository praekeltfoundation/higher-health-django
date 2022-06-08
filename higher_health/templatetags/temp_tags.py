from django import template
from django.conf import settings

register = template.Library()


@register.filter(name="field_type")
def field_type(field):
    return field.field.widget.__class__.__name__


@register.simple_tag
def is_maintenance_mode():
    return getattr(settings, "MAINTENANCE_MODE", False)
