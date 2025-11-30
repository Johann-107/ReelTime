# accounts/views.py
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
from django.http import JsonResponse
from django.urls import reverse


# --------------------------
# Admin Registration
# --------------------------
def register_admin(request):
    if request.method == "POST":
        cinema_name = request.POST.get("cinema_name")
        email = request.POST.get("email")

        if not cinema_name or not email:
            message = "Please provide both cinema name and email."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': message
                }, status=400)
            else:
                messages.error(request, message)
                return redirect("register_admin")

        # Check if email already exists in PendingAdmin
        pending, created = PendingAdmin.objects.get_or_create(
            email=email,
            defaults={
                "cinema_name": cinema_name,
                "token": get_random_string(48),
            },
        )

        # Send or resend confirmation email (synchronous)
        confirmation_link = request.build_absolute_uri(f"/accounts/confirm-admin/{pending.token}/")

        if not created:
            if pending.is_confirmed:
                message = "This email is already confirmed as an admin."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': message,
                        'redirect_url': reverse('login')
                    })
                else:
                    messages.error(request, message)
                    return redirect("login")
            else:
                pending.cinema_name = cinema_name
                pending.token = get_random_string(48)
                pending.save()
                message = "A new confirmation link has been sent to your email."
                email_sent = send_admin_confirmation_email(email, confirmation_link, cinema_name)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': message
                    })
                else:
                    messages.info(request, message)

        else:
            message = "A confirmation email has been sent. Please check your inbox."
            email_sent = send_admin_confirmation_email(email, confirmation_link, cinema_name)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': message
                })
            else:
                messages.success(request, message)
        
        if not email_sent:
            message = "Confirmation email could not be sent. Please try again."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': message
                }, status=500)
            else:
                messages.error(request, message)
                return redirect("register_admin")
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message
            })
        else:
            return redirect("register_admin")

    # Handle GET requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'GET request not allowed'}, status=405)
    else:
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

    # Send credentials to the admin email (synchronous)
    email_sent = send_admin_credentials_email(pending.email, pending.cinema_name, admin.username)
    
    if not email_sent:
        messages.warning(request, "Admin account created but credentials email failed to send. Please contact support.")
    else:
        messages.success(request, "Admin account confirmed! Login details have been sent to your email.")
    
    # Mark as confirmed instead of deleting
    pending.is_confirmed = True
    pending.save()

    return redirect("login")


# --------------------------
# User Registration
# --------------------------

def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                print("User created:", user.username)
                
                messages.success(request, "Registration successful! Please log in.")
                
                # Check if it's an AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Registration successful! Please log in.',
                        'redirect_url': '/?show_login=true'
                    })
                else:
                    # Regular form submission
                    return redirect('login')
                    
            except Exception as e:
                print("Error during user creation:", str(e))
                # Handle unique constraint errors (like duplicate email)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {'email': [{'message': 'This email is already registered. Please use a different email or log in.'}]}
                    }, status=400)
                else:
                    messages.error(request, "This email is already registered. Please use a different email or log in.")
                    return render(request, 'accounts/register.html', {'form': form})
        else:
            # Form has errors
            print("Form errors:", form.errors)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON errors for AJAX
                return JsonResponse({
                    'success': False,
                    'errors': form.errors.get_json_data()
                }, status=400)
            else:
                # Regular form submission with errors
                return render(request, 'accounts/register.html', {'form': form})
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
            return redirect('/?show_login=true')  # Redirect to index with login modal

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
        return redirect('/?show_login=true&login_error=1')  # Redirect to index with login modal

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
# --------------------------
# Logout
# --------------------------
@login_required
def logout_user(request):
    username = request.user.username
    logout(request)
    request.session.flush()
    messages.info(request, f"Goodbye {username}! You have been logged out successfully.")
    return redirect('index')