from django.shortcuts import render, redirect


# views.py
import random
import time
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User

def send_email_otp(request):
    if request.method == "POST":
        email = request.POST.get("email").strip().lower()

        # Generate 4-digit OTP
        otp = str(random.randint(1000, 9999))

        # Store OTP & timestamp in session
        request.session['otp'] = otp
        request.session['otp_email'] = email
        request.session['otp_time'] = time.time()

        # Send email
        send_mail(
            "Your Login OTP",
            f"Your OTP is: {otp}\n\nIt will expire in 3 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

        messages.success(request, "OTP sent to your email.")
        return redirect('verify_email_otp')

    return redirect('index')

def verify_email_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        session_otp = request.session.get('otp')
        otp_email = request.session.get('otp_email')
        otp_time = request.session.get('otp_time')

        if not session_otp or not otp_email or not otp_time:
            messages.error(request, "Session expired. Please request OTP again.")
            return redirect('index')

        # Check expiry (3 minutes = 180 seconds)
        if time.time() - otp_time > 180:
            messages.error(request, "OTP expired. Please request a new one.")
            request.session.flush()  # Clear session
            return redirect('index')

        if entered_otp == session_otp:
            user, created = User.objects.get_or_create(
                username=otp_email,
                defaults={"email": otp_email, "is_active": True}
            )
            login(request, user)
            request.session.flush()  # Clear session after login
            messages.success(request, "Login successful!")
            return redirect('user')
        else:
            messages.error(request, "Invalid OTP.")
            return redirect('verify_email_otp')

    return render(request, 'verify_email_otp.html')

def index(request):
    return render(request, 'index.html')

def user(request):
    return render(request, 'user.html', {'user': request.user})