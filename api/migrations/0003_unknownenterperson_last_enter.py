# Generated by Django 4.1.7 on 2023-03-08 15:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_person_last_enter'),
    ]

    operations = [
        migrations.AddField(
            model_name='unknownenterperson',
            name='last_enter',
            field=models.TimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Последний вход человека'),
        ),
    ]
