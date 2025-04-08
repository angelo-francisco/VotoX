from celery import shared_task

from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.core.mail import send_mail



@shared_task
def custom_send_email(subject, template, context, recipient_list):

    context["site_name"] = settings.SITE_NAME

    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )