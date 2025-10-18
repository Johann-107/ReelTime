from accounts.utils import create_default_admin
from accounts.models import User
from accounts.forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash

# --------------------------
# Admin Registration
# --------------------------
def register_admin(request):
    if request.method == 'POST':
        cinema_name = request.POST.get('cinema_name')

        if not cinema_name:
            return redirect('register_admin')

        # Create default admin for that cinema
        create_default_admin(cinema_name)
        request.session['admin_registration_success'] = True
        return redirect('login')

    return render(request, 'accounts/register_admin.html')


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
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

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
# Edit Profile
# --------------------------
@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.save()

        request.session['profile_updated'] = True
        return redirect('profile')

    return render(request, 'accounts/edit_profile.html', {'user': user})


# --------------------------
# Logout
# --------------------------
@login_required
def logout_user(request):
    logout(request)
    request.session.flush()
    request.session['logout_success'] = True
    return redirect('login')
