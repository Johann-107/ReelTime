from django.shortcuts import render
from django.http import HttpResponse
from .forms import RegisterForm

# Create your views here.
def home(request):
    return render(request, 'reel_time/home.html')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            
            # Sign up user in Supabase Auth
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Optionally store extra info in Supabase table
                supabase.table("profiles").insert({
                    "id": response.user.id,
                    "username": username,
                    "email": email
                }).execute()

                return redirect('login')  # Redirect to login page
            else:
                error = response.get("error", {}).get("message", "Registration failed")
                return render(request, "reel_time/register.html", {"form": form, "error": error})
    else:
        form = RegisterForm()
    
    return render(request, "reel_time/register.html", {"form": form})