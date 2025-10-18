from django import forms
from .models import Movie

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = [
            'title', 'description', 'release_date', 'end_date',
            'showing_times', 'poster', 'genre', 'director',
            'duration_minutes', 'rating'
        ]
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'showing_times': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g. ["10:00 AM", "1:30 PM", "6:45 PM"]'}),
        }
