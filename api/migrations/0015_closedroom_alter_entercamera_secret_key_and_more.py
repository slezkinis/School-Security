# Generated by Django 4.1.7 on 2024-09-20 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_employee_student_delete_person_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClosedRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('secret_key', models.CharField(max_length=100, verbose_name='Секретный ключ камеры')),
            ],
            options={
                'verbose_name': 'Комната с замком',
                'verbose_name_plural': 'Комнаты с замком',
            },
        ),
        migrations.AlterField(
            model_name='entercamera',
            name='secret_key',
            field=models.CharField(default='o4e9ojdp', max_length=100, verbose_name='Секретный ключ камеры'),
        ),
        migrations.AlterField(
            model_name='exitcamera',
            name='secret_key',
            field=models.CharField(max_length=100, verbose_name='Секретный ключ камеры'),
        ),
    ]
