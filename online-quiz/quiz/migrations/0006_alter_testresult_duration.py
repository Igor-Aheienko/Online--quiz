# Generated by Django 5.1.6 on 2025-06-15 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_testresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='duration',
            field=models.IntegerField(default=0),
        ),
    ]
