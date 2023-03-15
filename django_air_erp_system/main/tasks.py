from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_mail_task(message, email, mail_subject):
    try:
        from_email = getattr(settings, 'EMAIL_HOST_USER')
    except AttributeError:
        raise AttributeError(
            'You must add EMAIL_HOST_USER attribute to your settings')
    send_mail(
        subject=mail_subject,
        message=message,
        from_email=from_email,
        recipient_list=[email],
        fail_silently=True,
    )
