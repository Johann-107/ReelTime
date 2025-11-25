from django import forms
from .models import Movie, MovieAdminDetails
from django.forms.widgets import DateInput, Textarea
from halls.models import Hall
import json


class MovieAdminDetailsForm(forms.ModelForm):
    class Meta:
        model = MovieAdminDetails
        fields = ['release_date', 'end_date', 'hall', 'showing_times', 'poster', 'price']  # Added price field
        widgets = {
            'release_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
            'showing_times': Textarea(attrs={'rows': 2, 'placeholder': 'e.g. ["10:00 AM", "1:30 PM"]'}),
            'price': forms.NumberInput(attrs={'step': '1.00', 'min': '0'}),
        }

    # Edited here: Added __init__ to convert showing_times format for display
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Convert showing_times to simple format for display
        if self.instance.pk and self.instance.showing_times:
            if isinstance(self.instance.showing_times, list) and len(self.instance.showing_times) > 0:
                if isinstance(self.instance.showing_times[0], dict):
                    # Extract just the times
                    simple_times = [s['time'] for s in self.instance.showing_times]
                    # Format as simple readable string
                    self.initial['showing_times'] = str(simple_times)

    # Edited here: Added clean_showing_times to convert simple times to full format with max_seats
    def clean_showing_times(self):
        data = self.cleaned_data.get('showing_times')
        
        if not data:
            return []
        
        # If it's already a list, check if it needs conversion
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                return data  # Already in full format
            else:
                # Convert simple list to full format
                hall = self.cleaned_data.get('hall') or self.instance.hall
                return [{"time": t, "max_seats": hall.capacity} for t in data]
        
        # Parse JSON string
        try:
            parsed = json.loads(data)
            
            if not isinstance(parsed, list):
                raise forms.ValidationError("Showing times must be a JSON list.")
            
            # Convert simple times to full format with hall capacity
            hall = self.cleaned_data.get('hall') or self.instance.hall
            full_showtimes = [{"time": t, "max_seats": hall.capacity} for t in parsed]
            
            return full_showtimes
            
        except json.JSONDecodeError:
            raise forms.ValidationError('Enter a valid JSON.')
        except Exception:
            raise forms.ValidationError('Enter showtimes as a JSON list, e.g. ["10:00 AM", "1:30 PM"]')


class MovieForm(forms.ModelForm):
    # Extra fields for admin details
    release_date = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    hall = forms.ModelChoiceField(queryset=Hall.objects.all(), required=True)
    price = forms.DecimalField(  # Added price field
        max_digits=6, 
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '1.00', 'min': '0'}),
        required=True,
        help_text="Price per seat"
    )

    # Admin enters only the showtime list (simple)
    showing_times = forms.CharField(
        widget=Textarea(attrs={'rows': 2, 'placeholder': 'e.g. ["10:00 AM", "1:30 PM", "6:45 PM"]'}),
        required=False
    )

    poster = forms.ImageField(required=False)

    class Meta:
        model = Movie
        fields = [
            'title', 'description',
            'genre', 'director', 'duration_minutes', 'rating',
        ]

    def __init__(self, *args, **kwargs):
        self.admin = kwargs.pop('admin', None)
        super().__init__(*args, **kwargs)

        # Load existing MovieAdminDetails data
        if self.instance.pk and self.admin:
            try:
                admin_details = self.instance.admin_details.get(admin=self.admin)

                self.fields['release_date'].initial = admin_details.release_date
                self.fields['end_date'].initial = admin_details.end_date
                self.fields['hall'].initial = admin_details.hall
                self.fields['price'].initial = admin_details.price  # Added price field
                self.fields['poster'].initial = admin_details.poster

                # Convert stored full showtime objects into simple ["10 AM", ...]
                simple_times = [s['time'] for s in admin_details.showing_times]
                self.fields['showing_times'].initial = json.dumps(simple_times)

            except MovieAdminDetails.DoesNotExist:
                pass

    # ------------------------------
    # CLEAN SHOWING TIMES INPUT
    # Admin inputs simple: ["10:00 AM", "1:30 PM"]
    # ------------------------------
    def clean_showing_times(self):
        data = self.cleaned_data['showing_times']

        if not data:
            return []

        try:
            parsed = json.loads(data)

            if not isinstance(parsed, list):
                raise forms.ValidationError("Showing times must be a JSON list.")

            for time in parsed:
                if not isinstance(time, str):
                    raise forms.ValidationError("Each showtime must be a string.")

            return parsed  # simple list
        except Exception:
            raise forms.ValidationError('Enter showtimes as a JSON list, e.g. ["10:00 AM", "1:30 PM"]')

    # ------------------------------
    # SAVE
    # ------------------------------
    def save(self, commit=True):
        movie = super().save(commit=commit)

        if self.admin:
            hall = self.cleaned_data['hall']
            simple_times = self.cleaned_data['showing_times']
            price = self.cleaned_data['price']  # Added price field

            # Convert to full showtime objects with hall capacity
            full_showtimes = [
                {"time": t, "max_seats": hall.capacity}
                for t in simple_times
            ]

            # Save or update MovieAdminDetails
            admin_details, created = MovieAdminDetails.objects.get_or_create(
                movie=movie,
                admin=self.admin,
                defaults={
                    'release_date': self.cleaned_data['release_date'],
                    'end_date': self.cleaned_data['end_date'],
                    'hall': hall,
                    'price': price,  # Added price field
                    'showing_times': full_showtimes,
                    'poster': self.cleaned_data.get('poster'),
                }
            )

            if not created:
                admin_details.release_date = self.cleaned_data['release_date']
                admin_details.end_date = self.cleaned_data['end_date']
                admin_details.hall = hall
                admin_details.price = price  # Added price field
                admin_details.showing_times = full_showtimes

                if self.cleaned_data.get('poster'):
                    admin_details.poster = self.cleaned_data['poster']

                admin_details.save()

        return movie