from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .models import ClusterAdmin, District

from django.contrib.auth import authenticate, login
from django.core.cache import cache


def superadmin(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        primary_mobile = request.POST.get('primary_mobile')
        alternative_mobile = request.POST.get('alternative_mobile')
        district_ids = request.POST.getlist('districts')
        id_proof = request.FILES.get('id_proof')
        passport_photo = request.FILES.get('passport_photo')

        # Check if email already exists
        if ClusterAdmin.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered as a Cluster Admin.")
            return redirect('superadmin')

        # Double-check if any district is already assigned
        already_taken = District.objects.filter(id__in=district_ids, assigned_cluster_admins__isnull=False)
        if already_taken.exists():
            names = ", ".join(d.name for d in already_taken)
            messages.error(request, f"The following districts are already assigned: {names}")
            return redirect('superadmin')

        # Create ClusterAdmin object
        cluster_admin = ClusterAdmin.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            primary_mobile=primary_mobile,
            alternative_mobile=alternative_mobile,
            id_proof=id_proof,
            passport_photo=passport_photo,
            is_appointed=True,
            is_accepted=True  # Directly mark as accepted
        )
        cluster_admin.districts.set(District.objects.filter(id__in=district_ids))

        # Create username & password
        alt_mobile = alternative_mobile if alternative_mobile else ''
        last4 = alt_mobile[-4:] if len(alt_mobile) >= 4 else alt_mobile
        username = f"{first_name}{last_name}{last4}".lower().replace(" ", "")
        password = get_random_string(10)

        # Create linked user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        cluster_admin.user = user
        cluster_admin.save()

        # Send email with credentials
        message = f"""
Dear {first_name},

Congratulations! You have been appointed as a Cluster Admin.

Here are your login credentials:

Username: {username}
Password: {password}

Please login and change your password immediately.

Regards,
SuperAdmin Team
        """
        send_mail(
            subject="Cluster Admin Appointment & Login Credentials",
            message=message,
            from_email="ebookcommunuty@gmail.com",
            recipient_list=[email],
        )

        messages.success(request, f"Appointment successful. Credentials sent to {email}.")
        return redirect('superadmin')

    # GET request
    districts = District.objects.all()
    assigned_ids = set(
        District.objects.filter(assigned_cluster_admins__isnull=False)
        .values_list('id', flat=True)
    )

    return render(request, 'cluster/superadmin.html', {
        'districts': districts,
        'assigned_ids': assigned_ids,
    })



OTP_EXPIRY_SECONDS = 300  # 5 minutes

def cluster_admin_login(request):
    pending_user_id = request.session.get('pending_user_id')

    if request.method == "POST":
        # OTP verification step
        if pending_user_id and 'otp' in request.POST:
            entered_otp = request.POST.get('otp')
            cached_otp = cache.get(f'otp_{pending_user_id}')

            if cached_otp == entered_otp:
                user = User.objects.get(pk=pending_user_id)
                login(request, user)
                request.session.pop('pending_user_id', None)
                cache.delete(f'otp_{pending_user_id}')
                messages.success(request, "Login successful!")
                return redirect('cluster_admin_dashboard')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return render(request, 'cluster/admin_login.html', {'otp_required': True})

        # Username/password step
        else:
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                otp = get_random_string(6, allowed_chars='0123456789')
                cache.set(f'otp_{user.pk}', otp, OTP_EXPIRY_SECONDS)
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is: {otp}',
                    'ebookcommunuty@gmail.com',
                    [user.email],
                )
                request.session['pending_user_id'] = user.pk
                messages.success(request, f"OTP sent to {user.email}")
                return render(request, 'cluster/admin_login.html', {'otp_required': True})
            else:
                messages.error(request, "Invalid email or password.")

    # GET request: show normal login form and clear OTP session
    request.session.pop('pending_user_id', None)
    return render(request, 'cluster/admin_login.html', {'otp_required': False})


from django.shortcuts import render
from .models import ClusterAdmin, District

def cluster_admin_dashboard(request):
    cluster_admin = ClusterAdmin.objects.get(user=request.user)
    districts = cluster_admin.districts.all()


    context = {
        'cluster_admin_name': f"{cluster_admin.first_name} {cluster_admin.last_name}",
        'districts': districts,
    }
    return render(request, 'cluster/cluster_admin_dashboard.html', context)
