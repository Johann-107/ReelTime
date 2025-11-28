from accounts.models import User, PendingAdmin
from accounts.forms import RegistrationForm, UserProfileForm
from accounts.utils import (
    create_default_admin, 
    send_admin_confirmation_email, 
    send_admin_credentials_email
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.utils.crypto import get_random_string
from django.conf import settings
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

        # Send or resend confirmation email using threading
        confirmation_link = request.build_absolute_uri(f"/accounts/confirm-admin/{pending.token}/")
        send_admin_confirmation_email(email, confirmation_link, cinema_name)
        
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

    # Check if already confirmed
    if pending.is_confirmed:
        messages.info(request, "This admin account has already been confirmed.")
        return redirect("login")

    # Create the default admin
    admin = create_default_admin(pending.cinema_name, pending.email)

    # Send credentials to the admin email using threading
    send_admin_credentials_email(pending.email, pending.cinema_name, admin.username)

    # Mark as confirmed instead of deleting
    pending.is_confirmed = True
    pending.save()

    messages.success(request, "Admin account confirmed! Login details have been sent to your email.")
    return redirect("login")


# --------------------------
# User Registration
# --------------------------
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Optional: Send welcome email using threading
            # send_welcome_email(user.email, user.username)
            
            request.session['registration_success'] = True
            messages.success(request, "Registration successful! Please log in.")
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
        username_or_email = request.POST.get('username_or_email', '').strip()
        password = request.POST.get('password', '').strip()

        if not username_or_email or not password:
            messages.error(request, "Please provide both username/email and password.")
            return render(request, 'accounts/login.html')

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
                messages.info(request, "Please change your password to continue.")
                return redirect('change_password')
            elif user.is_admin:
                messages.success(request, f"Welcome back, {user.cinema_name} Admin!")
                return redirect('admin_dashboard')
            else:
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('user_dashboard')

        messages.error(request, "Invalid username/email or password.")
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

        if not new_password or not confirm_password:
            messages.error(request, "Please fill in all password fields.")
            return render(request, 'accounts/change_password.html')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/change_password.html')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/change_password.html')

        user.set_password(new_password)
        user.must_change_password = False
        user.save()

        # Keep user logged in
        update_session_auth_hash(request, user)

        messages.success(request, "Password changed successfully!")
        return redirect('admin_dashboard' if user.is_admin else 'user_dashboard')

    return render(request, 'accounts/change_password.html')


# --------------------------
# Profile View
# --------------------------
@login_required
def profile_view(request):
    profile_updated = request.session.pop('profile_updated', False)
    
    if profile_updated:
        messages.success(request, "Profile updated successfully!")

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
                    messages.error(request, f"{field.title().replace('_', ' ')}: {error}")
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
    username = request.user.username
    logout(request)
    request.session.flush()
    request.session['logout_success'] = True
    messages.info(request, f"Goodbye {username}! You have been logged out successfully.")
    return redirect('login')