from accounts.utils import create_default_admin, get_logged_in_user
from accounts.models import User
from accounts.forms import RegistrationForm
from accounts.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password


# Admin Registration
def register_admin(request):
    if request.method == 'POST':
        cinema_name = request.POST.get('cinema_name')

        # Create default admin for that cinema
        admin = create_default_admin(cinema_name)

        messages.success(request, f"Default admin account created for {cinema_name}: {admin.username}")
        return redirect('login')

    return render(request, 'accounts/register_admin.html')


# User Registration
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # or wherever you want to redirect
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


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

    return render(request, 'accounts/login.html')


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

    return render(request, 'accounts/change_password.html')


@login_required
def profile_view(request):
    user = get_logged_in_user(request)
    return render(request, 'accounts/profile.html', {'user': user})


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

    return render(request, 'accounts/edit_profile.html', {'user': user})


@login_required
def logout_user(request):
    request.session.flush()  # clears session
    return redirect('login')