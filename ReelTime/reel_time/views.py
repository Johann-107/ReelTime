from django.shortcuts import render

# Create your views here.
# Home view
def home(request):
    return render(request, 'reel_time/index.html')