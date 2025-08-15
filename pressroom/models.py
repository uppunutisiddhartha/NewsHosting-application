 # models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta

# --- existing models you already had (EmailOTP, Reporter, Address, EmailVerificationToken) ---
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
    phone = models.CharField(max_length=15)
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
            self.expires_at = timezone.now() + timedelta(days=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Verification token for {self.reporter.email}"

# --- District model remains ---
class District(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# --- SINGLE ClusterAdmin model (remove any duplicate ClusterAdmin class in your file) ---
class ClusterAdmin(models.Model):
    
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    # districts the cluster admin manages
    districts = models.ManyToManyField(District, related_name="assigned_cluster_admins", blank=True)  # one-to-many relationship
    alternative_mobile = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    id_proof = models.FileField(upload_to='id_proofs/', blank=True, null=True)
    profile_picture= models.ImageField(upload_to='passport_photos/', blank=True, null=True)
    is_appointed = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        # fallback to user if available
        if self.user:
            return f"Cluster Admin - {self.user.get_full_name()}"
        return f"Cluster Admin - {self.first_name} {self.last_name}"


class News(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    video = models.FileField(upload_to='news_videos/', blank=True, null=True)
    content = models.TextField()

    District = models.ForeignKey(District, on_delete=models.CASCADE, related_name='news_items')
    mandal = models.CharField(max_length=100)
    breaking_news = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE, related_name='news_items', null=True, blank=True)

    def __str__(self):
        return self.title



  