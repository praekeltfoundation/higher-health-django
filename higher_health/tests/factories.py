import factory

from higher_health import models


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
