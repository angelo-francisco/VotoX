# Generated by Django 5.2 on 2025-04-08 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_verificationcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='verificationcode',
            name='purpose',
            field=models.CharField(blank=True, choices=[('VA', 'Verify-Account')], max_length=5, null=True),
        ),
    ]
