from .utils import create_default_admin
from .models import User
from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from functools import wraps

# Create your views here.
# Home view
def home(request):
    return render(request, 'reel_time/index.html')


# Admin Registration
def register_admin(request):
    if request.method == 'POST':
        cinema_name = request.POST.get('cinema_name')

        # Create default admin for that cinema
        admin = create_default_admin(cinema_name)

        messages.success(request, f"Default admin account created for {cinema_name}: {admin.username}")
        return redirect('login')

    return render(request, 'reel_time/register_admin.html')


# User Registration
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # or wherever you want to redirect
    else:
        form = RegistrationForm()
    return render(request, 'reel_time/register.html', {'form': form})


# User Login
def login_user(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # Try to find user by username or email
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect('login')

        # Check password
        if check_password(password, user.password):
            # Set session
            request.session['user_id'] = user.id
            request.session['username'] = user.username

            if user.must_change_password:
                return redirect('change_password') # force password change
            
            if user.is_admin:
                return redirect('admin_dashboard')  # admin dashboard
            else:
                return redirect('user_dashboard')  # home page
        else:
            # messages.error(request, "Invalid password.")
            return redirect('login')

    return render(request, 'reel_time/login.html')


# Change Password
def change_password(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user.password = make_password(new_password)
            user.must_change_password = False
            user.save()
            messages.success(request, "Password updated successfully!")
            return redirect('admin_dashboard' if user.is_admin else 'user_dashboard')

    return render(request, 'reel_time/change_password.html')


# Decorator to require admin
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
        user = User.objects.get(id=user_id)
        if not user.is_admin:
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# Decorator to require login
def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def profile_view(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    return render(request, 'reel_time/profile.html', {'user': user})


@login_required
def edit_profile(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Update user info
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()

        # ✅ Update session username so dashboard reflects the change
        request.session['username'] = user.username

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'reel_time/edit_profile.html', {'user': user})


@login_required
def user_dashboard(request):
    username = request.session.get('username')
    return render(request, 'reel_time/user_dashboard.html', {'username': username})


@admin_required
def admin_dashboard(request):
    return render(request, 'reel_time/admin_dashboard.html')


def logout_user(request):
    request.session.flush()  # clears session
    return redirect('login')