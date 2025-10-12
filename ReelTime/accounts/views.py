from accounts.utils import create_default_admin, get_logged_in_user
from accounts.models import User
from accounts.forms import RegistrationForm
from accounts.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model

User = get_user_model()


# Admin Registration
def register_admin(request):
    if request.method == 'POST':
        cinema_name = request.POST.get('cinema_name')

        if not cinema_name:
            # messages.warning(request, "Please enter a cinema name.")
            return redirect('register_admin')

        # Create default admin for that cinema
        admin = create_default_admin(cinema_name)
        # messages.success(request, f"✅ Default admin account created for {cinema_name}: {admin.username}")
        request.session['admin_registration_success'] = True
        return redirect('login')

    return render(request, 'accounts/register_admin.html')


# User Registration
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


# User Login
def login_user(request):
    registration_success = request.session.pop('registration_success', False)
    admin_registration_success = request.session.pop('admin_registration_success', False)
    invalid_credentials = request.session.pop('invalid_credentials', False)
    user_not_found = request.session.pop('user_not_found', False)
    logout_success = request.session.pop('logout_success', False)

    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # Try username first
        user = authenticate(request, username=username_or_email, password=password)

        # If that fails, try email
        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                request.session['user_not_found'] = True
                user = None

        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['is_admin'] = user.is_admin
            print("✅ Logged in:", user.username, "| Admin:", user.is_admin)
            print("Session Keys:", list(request.session.keys()))
            if user.must_change_password:
                return redirect('change_password')
            elif user.is_admin:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')

        else:
            return render(request, 'accounts/login.html', {
                'invalid_credentials': True
            })

    return render(
        request,
        'accounts/login.html',
        {
            'registration_success': registration_success,
            'admin_registration_success': admin_registration_success,
            'invalid_credentials': invalid_credentials,
            'user_not_found': user_not_found,
            'logout_success': logout_success,
        }
    )



# Change Password
def change_password(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
             # messages.warning(request, "⚠️ Passwords do not match.")
        # else:
            user.password = make_password(new_password)
            user.must_change_password = False
            user.save()
            # messages.success(request, "✅ Password updated successfully!")
            return redirect('admin_dashboard' if request.session.get('is_admin') else 'user_dashboard')

    return render(request, 'accounts/change_password.html')

@login_required
def profile_view(request):
    user = get_logged_in_user(request)
    
    # Check if profile was just updated
    profile_updated = request.session.pop('profile_updated', False)
    
    return render(request, 'accounts/profile.html', {
        'user': user,
        'profile_updated': profile_updated
    })


@login_required
def edit_profile(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.phone_number = request.POST.get('phone_number')
        user.save()

        request.session['username'] = user.username
        request.session['profile_updated'] = True
        return redirect('profile')

    return render(request, 'accounts/edit_profile.html', {'user': user})


@login_required
def logout_user(request):
    # Clear Django authentication
    logout(request)

    # Clear your custom session keys
    request.session.pop('user_id', None)
    request.session.pop('username', None)
    request.session.pop('is_admin', None)
    request.session.pop('profile_updated', None)

    # Optionally flush all session data completely
    request.session.flush()  # This ensures total logout (recommended)

    request.session['logout_success'] = True
    return redirect('login')