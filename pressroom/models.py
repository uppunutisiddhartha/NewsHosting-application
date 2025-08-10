# models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta



class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=3)

class Reporter(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='reporters/profile_pictures/')
    idproof = models.FileField(upload_to='reporters/idproofs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    rejection_reason = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Address(models.Model):
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)
    district = models.CharField(max_length=100)
    mandal = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    is_default = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.state}, {self.city}"



class EmailVerificationToken(models.Model):
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=1)  # token valid for 1 day
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Verification token for {self.reporter.email}"