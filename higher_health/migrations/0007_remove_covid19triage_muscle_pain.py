# Generated by Django 2.2.12 on 2020-05-19 09:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('higher_health', '0006_remove_covid19triage_history_other'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='covid19triage',
            name='muscle_pain',
        ),
    ]
