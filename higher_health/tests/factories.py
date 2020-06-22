from django.contrib.auth.models import User

import factory

from higher_health import models


class UserFactory(factory.DjangoModelFactory):
    first_name = "first_name"
    last_name = "last_name"
    username = "username"
    _password = "password"

    class Meta:
        model = User
        django_get_or_create = ("username",)

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        instance.set_password(cls._password)


class UniversityFactory(factory.DjangoModelFactory):
    name = "University"
    province = "ZA-WC"

    class Meta:
        model = models.University


class CampusFactory(factory.DjangoModelFactory):
    name = "Campus"
    university = factory.SubFactory(UniversityFactory)

    class Meta:
        model = models.Campus
