# Generated by Django 2.2.12 on 2020-05-15 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('higher_health', '0004_auto_20200514_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='covid19triage',
            name='facility_destination_province',
        ),
        migrations.AlterField(
            model_name='covid19triage',
            name='history_other',
            field=models.SmallIntegerField(choices=[(1, 'Yes'), (2, 'No'), (3, 'Maybe')], default=2),
        ),
    ]
