# Generated by Django 2.2.12 on 2020-06-04 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("higher_health", "0008_change_meta_options")]

    operations = [
        migrations.AlterModelOptions(
            name="campus",
            options={"ordering": ("name",), "verbose_name_plural": "Campuses"},
        ),
        migrations.AlterModelOptions(
            name="university",
            options={"ordering": ("name",), "verbose_name_plural": "Universities"},
        ),
    ]
