from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import *
from .utils import send_email  # ✅ Centralized email sender

# Reporter registration with email verification
def reporter_registration(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        profile_picture = request.FILES.get("profile_picture")
        idproof = request.FILES.get("idproof")

        district = request.POST.get("district")
        mandal = request.POST.get("mandal")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postal_code = request.POST.get("postal_code")
        country = request.POST.get("country")
        phone_number = request.POST.get("phone_number")

        if User.objects.filter(username=phone).exists():
            messages.error(request, "This phone number is already registered.")
            return redirect('reporter_registration')

        user = User.objects.create_user(
            username=phone,
            password=password,
            email=email,
            first_name=name
        )
        reporter_obj = Reporter.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            profile_picture=profile_picture,
            idproof=idproof,
            email_verified=False,
        )

        Address.objects.create(
            reporter=reporter_obj,
            district=district,
            mandal=mandal,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            phone_number=phone_number,
            is_default=True
        )

        token_obj = EmailVerificationToken.objects.create(reporter=reporter_obj)
        verification_url = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': str(token_obj.token)})
        )

        send_email(
            subject="Verify your Reporter Email",
            message=(
                f"Hello {name},\n\n"
                f"Please verify your email address by clicking the link below:\n"
                f"{verification_url}\n\n"
                f"This link will expire in 24 hours."
            ),
            recipient_list=[email]
        )

        messages.success(request, "Registration successful! Please check your email to verify your account.")
        return redirect('reporter_registration')

    return render(request, "reporter_registration.html")


def verify_email(request, token):
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "Invalid or expired verification link.")
        return redirect('reporter_registration')

    if token_obj.expires_at < timezone.now():
        messages.error(request, "Verification link expired. Please register again.")
        return redirect('reporter_registration')

    reporter = token_obj.reporter
    reporter.email_verified = True
    reporter.save()
    token_obj.delete()

    messages.success(request, "Email verified! You can now log in.")
    return redirect('reporter_login')


def reporter_admin_view(request):
    reporters = Reporter.objects.all().order_by("-date_joined")
    return render(request, "reporter_admin.html", {"reporters": reporters})


@require_POST
def handle_reporter_status(request, reporter_id):
    reporter_obj = get_object_or_404(Reporter, id=reporter_id)
    action = request.POST.get("action")

    if action == "approve":
        reporter_obj.status = "Approved"
        reporter_obj.rejection_reason = None
        subject = "Reporter Application Approved"
        message = "Your application has been approved. You can now log in."
    elif action == "reject":
        reason = request.POST.get("rejection_reason", "No reason provided")
        reporter_obj.status = "Rejected"
        reporter_obj.rejection_reason = reason
        subject = "Reporter Application Rejected"
        message = f"Your application was rejected. Reason: {reason}"
    else:
        return redirect("reporter_admin_dashboard")

    reporter_obj.save()

    send_email(subject, message, [reporter_obj.email])

    return redirect("reporter_admin_dashboard")


def reporter_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            reporter = getattr(user, 'reporter', None)
            if reporter:
                if reporter.status == "Approved":
                    login(request, user)
                    return redirect("news_posting")
                elif reporter.status == "Pending":
                    messages.info(request, "Your registration is still pending approval.")
                elif reporter.status == "Rejected":
                    messages.error(request, "Your registration has been rejected.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "reporter_login.html")


def news_posting(request):
    if not request.user.is_authenticated:
        return redirect("reporter_login")

    reporter = request.user.reporter
    districts = District.objects.all() 
    return render(request, "news_posting.html", {"districts": districts, "reporter": reporter})


def posting_news(request):
    districts = District.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        district_id = request.POST.get("district")
        mandal = request.POST.get("mandal")
        image = request.FILES.get("image")
        video = request.FILES.get("video")
        breaking_news = request.POST.get("breaking_news") == "on"

        district = District.objects.get(id=district_id)
        News.objects.create(
            reporter=request.user.reporter,
            title=title,
            content=content,
            District=district,
            mandal=mandal,
            image=image,
            video=video,
            breaking_news=breaking_news
        )

        return redirect("news_posting")

    return render(request, "news_posting.html", {"districts": districts})


def reporter_dashboard(request):
    reporter = Reporter.objects.get(user=request.user)
    return render(request, 'reporter_dashboard.html', {'reporter': reporter})
