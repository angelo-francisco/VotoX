# Generated by Django 5.2 on 2025-04-11 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0003_poll_stars'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='title',
            field=models.CharField(max_length=80),
        ),
    ]
