# Generated by Django 4.2.14 on 2024-08-14 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_series', '0027_alter_question_section_alter_question_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proctoringsession',
            name='status',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='question',
            name='section',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='question',
            name='status',
            field=models.CharField(max_length=50),
        ),
    ]
