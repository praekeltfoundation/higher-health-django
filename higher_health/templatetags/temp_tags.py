from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name="field_type")
def field_type(field):
    return field.field.widget.__class__.__name__


@register.filter
def expires(val, days, midnight=True):
    expire = val + timezone.timedelta(days=days)
    if midnight:
        expire.replace(second=59, minute=59, hour=23)
    return expire
