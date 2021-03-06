# Generated by Django 2.2.12 on 2020-06-22 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('higher_health', '0013_alter_field_province_on_university'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campus',
            options={'ordering': ('sort_order', 'name'), 'verbose_name_plural': 'Campuses'},
        ),
        migrations.AlterModelOptions(
            name='university',
            options={'ordering': ('sort_order', 'name'), 'verbose_name_plural': 'Universities'},
        ),
        migrations.AddField(
            model_name='campus',
            name='sort_order',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='university',
            name='sort_order',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
