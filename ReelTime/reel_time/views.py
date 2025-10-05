from .models import User
from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password

# Create your views here.
def home(request):
    return render(request, 'reel_time/index.html')


def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # or wherever you want to redirect
    else:
        form = RegistrationForm()
    return render(request, 'reel_time/register.html', {'form': form})


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
            messages.success(request, f"Welcome {user.username}!")
            return redirect('dashboard')  # home page
        else:
            messages.error(request, "Invalid password.")
            return redirect('login')

    return render(request, 'reel_time/login.html')


# Decorator to require login
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def dashboard(request):
    username = request.session.get('username')
    return render(request, 'reel_time/dashboard.html', {'username': username})


def logout_user(request):
    request.session.flush()  # clears session
    return redirect('login')