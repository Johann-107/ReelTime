from accounts.utils import create_default_admin
from accounts.models import User, PendingAdmin
from accounts.forms import RegistrationForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages


# --------------------------
# Admin Registration
# --------------------------
def register_admin(request):
    if request.method == "POST":
        cinema_name = request.POST.get("cinema_name")
        email = request.POST.get("email")

        if not cinema_name or not email:
            messages.error(request, "Please provide both cinema name and email.")
            return redirect("register_admin")

        # Check if email already exists in PendingAdmin
        pending, created = PendingAdmin.objects.get_or_create(
            email=email,
            defaults={
                "cinema_name": cinema_name,
                "token": get_random_string(48),
            },
        )

        if not created:
            if pending.is_confirmed:
                messages.error(request, "This email is already confirmed as an admin.")
                return redirect("login")
            else:
                # Update cinema name and regenerate token in case they want to retry
                pending.cinema_name = cinema_name
                pending.token = get_random_string(48)
                pending.save()
                messages.info(request, "A new confirmation link has been sent to your email.")

        else:
            messages.success(request, "A confirmation email has been sent. Please check your inbox.")

        # Send or resend confirmation email
        confirmation_link = request.build_absolute_uri(f"/accounts/confirm-admin/{pending.token}/")
        subject = "Confirm your admin registration - ReelTime"
        message = (
            f"Hello!\n\n"
            f"Did you register as admin for ReelTime?\n\n"
            f"If yes, please confirm by clicking this link:\n{confirmation_link}\n\n"
            f"If not, you can ignore this email."
        )

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return redirect("register_admin")

    return render(request, "accounts/register_admin.html")


# --------------------------
# Confirm Admin Registration
# --------------------------
def confirm_admin(request, token):
    try:
        pending = PendingAdmin.objects.get(token=token)
    except PendingAdmin.DoesNotExist:
        messages.error(request, "Invalid or expired confirmation link.")
        return redirect("register_admin")

    # Create the default admin
    admin = create_default_admin(pending.cinema_name, pending.email)

    # Send credentials to the admin email
    subject = "Your ReelTime Admin Account Credentials"
    message = (
        f"Your admin account for '{pending.cinema_name}' has been created!\n\n"
        f"Username: {admin.username}\n"
        f"Password: admin123\n\n"
        f"Please log in and change your password immediately."
    )

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [pending.email])

    # Mark as confirmed instead of deleting
    pending.is_confirmed = True
    pending.save()

    messages.success(request, "Admin account confirmed! Login details sent to your email.")
    return redirect("login")



# --------------------------
# User Registration
# --------------------------
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            request.session['registration_success'] = True
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


# --------------------------
# User Login
# --------------------------
def login_user(request):
    registration_success = request.session.pop('registration_success', False)
    admin_registration_success = request.session.pop('admin_registration_success', False)
    logout_success = request.session.pop('logout_success', False)

    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email').strip()
        password = request.POST.get('password').strip()

        # Try username first
        user = authenticate(request, username=username_or_email, password=password)

        # Try email if username fails
        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            if user.must_change_password:
                return redirect('change_password')
            elif user.is_admin:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')

        # Invalid credentials → reload login page
        return render(request, 'accounts/login.html', {'invalid_credentials': True})

    return render(
        request,
        'accounts/login.html',
        {
            'registration_success': registration_success,
            'admin_registration_success': admin_registration_success,
            'logout_success': logout_success,
        }
    )


# --------------------------
# Change Password
# --------------------------
@login_required
def change_password(request):
    user = request.user

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and confirm_password and new_password == confirm_password:
            user.set_password(new_password)
            user.must_change_password = False
            user.save()

            # Keep user logged in
            update_session_auth_hash(request, user)

            return redirect('admin_dashboard' if user.is_admin else 'user_dashboard')

    return render(request, 'accounts/change_password.html')


# --------------------------
# Profile View
# --------------------------
@login_required
def profile_view(request):
    profile_updated = request.session.pop('profile_updated', False)

    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile_updated': profile_updated
    })


# --------------------------
# Edit Profile (Updated with Cloudinary)
# --------------------------
@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        
        # Handle profile picture clearing
        clear_picture = request.POST.get('clear_profile_picture') == 'true'
        
        if form.is_valid():
            try:
                # Handle profile picture clearing
                if clear_picture and user.profile_picture:
                    user.profile_picture.delete()
                    user.profile_picture = None
                    user.save()
                    messages.success(request, "Profile picture removed successfully!")
                else:
                    # Save the form (Cloudinary will handle the upload automatically)
                    form.save()
                    messages.success(request, "Profile updated successfully!")
                
                request.session['profile_updated'] = True
                return redirect('profile')
                
            except Exception as e:
                messages.error(request, f"Error updating profile: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'user': user
    })


# --------------------------
# Logout
# --------------------------
@login_required
def logout_user(request):
    logout(request)
    request.session.flush()
    request.session['logout_success'] = True
    return redirect('login')
