# utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message, recipient_list, fail_silently=False):
    """
    Centralized email sending utility.
    Usage: send_email("Subject", "Body", ["recipient@example.com"])
    """
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=fail_silently
    )
