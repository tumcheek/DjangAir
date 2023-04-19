from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_mail_task(message: str, email: str, mail_subject: str) -> None:
    """
    Sends an email asynchronously using celery task.

    Args:
    - message: str: Email message.
    - email: str: Email recipient.
    - mail_subject: str: Email subject.

    Raises:
    - AttributeError: If EMAIL_HOST_USER attribute is not present in the settings.

    Returns: None.
    """
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
