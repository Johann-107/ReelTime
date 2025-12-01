from django import forms
from .models import Movie, MovieAdminDetails
from django.forms.widgets import DateInput, Textarea
from halls.models import Hall
import json
import cloudinary.uploader


class MovieAdminDetailsForm(forms.ModelForm):
    genre = forms.MultipleChoiceField(
        choices=Movie.GENRE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select up to 3 genres"
    )
    
    class Meta:
        model = MovieAdminDetails
        fields = ['release_date', 'end_date', 'hall', 'showing_times', 'poster', 'price']  # Added price field
        widgets = {
            'release_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
            'showing_times': Textarea(attrs={'rows': 2, 'placeholder': 'e.g. ["10:00 AM", "1:30 PM"]'}),
            'price': forms.NumberInput(attrs={'step': '1.00', 'min': '0'}),
        }
        help_texts = {
            'poster': 'Upload a poster image (JPG, PNG only, max 5MB)',
        }

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

    def clean_showing_times(self):
        data = self.cleaned_data.get('showing_times')
        
        if not data:
            return []
        
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                return data
            else:
                hall = self.cleaned_data.get('hall') or self.instance.hall
                return [{"time": t, "max_seats": hall.capacity} for t in data]
        
        try:
            parsed = json.loads(data)
            
            if not isinstance(parsed, list):
                raise forms.ValidationError("Showing times must be a JSON list.")
            
            hall = self.cleaned_data.get('hall') or self.instance.hall
            full_showtimes = [{"time": t, "max_seats": hall.capacity} for t in parsed]
            
            return full_showtimes
            
        except json.JSONDecodeError:
            raise forms.ValidationError('Enter a valid JSON.')
        except Exception:
            raise forms.ValidationError('Enter showtimes as a JSON list, e.g. ["10:00 AM", "1:30 PM"]')
    
    def clean_genre(self):
        genres = self.cleaned_data.get('genre')
        if genres and len(genres) > 3:
            raise forms.ValidationError("You can select a maximum of 3 genres.")
        return genres
    
    def clean_poster(self):
        poster = self.cleaned_data.get('poster')
        
        if poster and hasattr(poster, 'size'):
            # Validate file size (max 5MB)
            if poster.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 5MB )")
            
            # Validate file type
            valid_extensions = ['jpg', 'jpeg', 'png']
            extension = poster.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError("Unsupported file extension. Only JPG and PNG are allowed.")
        
        return poster
        
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

    showing_times = forms.CharField(
        widget=Textarea(attrs={'rows': 2, 'placeholder': 'e.g. ["10:00 AM", "1:30 PM", "6:45 PM"]'}),
        required=False
    )

    poster = forms.ImageField(
        required=False,
        help_text="Upload a poster image (JPG, PNG only, max 5MB)"
    )
    
    genre = forms.MultipleChoiceField(
        choices=Movie.GENRE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select up to 3 genres"
    )
    
    rating = forms.ChoiceField(
        choices=[('', 'Select Rating')] + Movie.RATING_CHOICES,
        widget=forms.Select,
        required=False,
        help_text="Select movie rating"
    )

    class Meta:
        model = Movie
        fields = [
            'title', 'description',
            'genre', 'director', 'duration_minutes', 'rating',
        ]

    def __init__(self, *args, **kwargs):
        self.admin = kwargs.pop('admin', None)
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.admin:
            try:
                admin_details = self.instance.admin_details.get(admin=self.admin)

                self.fields['release_date'].initial = admin_details.release_date
                self.fields['end_date'].initial = admin_details.end_date
                self.fields['hall'].initial = admin_details.hall
                self.fields['price'].initial = admin_details.price 
                self.fields['poster'].initial = admin_details.poster 

                simple_times = [s['time'] for s in admin_details.showing_times]
                self.fields['showing_times'].initial = json.dumps(simple_times)

            except MovieAdminDetails.DoesNotExist:
                pass

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
        
    def clean_genre(self):
        genres = self.cleaned_data.get('genre')
        if genres and len(genres) > 3:
            raise forms.ValidationError("You can select a maximum of 3 genres.")
        return genres
    
    def clean_poster(self):
        poster = self.cleaned_data.get('poster')
        
        if poster and hasattr(poster, 'size'):
            # Validate file size (max 5MB)
            if poster.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 5MB )")
            
            # Validate file type
            valid_extensions = ['jpg', 'jpeg', 'png']
            extension = poster.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError("Unsupported file extension. Only JPG and PNG are allowed.")
        
        return poster

    def save(self, commit=True):
        movie = super().save(commit=commit)

        if self.admin:
            hall = self.cleaned_data['hall']
            simple_times = self.cleaned_data['showing_times']
            price = self.cleaned_data['price']  # Added price field
            poster = self.cleaned_data.get('poster')

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
                    'poster': poster,
                }
            )

            if not created:
                admin_details.release_date = self.cleaned_data['release_date']
                admin_details.end_date = self.cleaned_data['end_date']
                admin_details.hall = hall
                admin_details.price = price 
                admin_details.showing_times = full_showtimes

                if poster:
                    # If there's an existing poster and we're uploading a new one,
                    # Cloudinary will automatically handle the replacement
                    admin_details.poster = poster

                admin_details.save()

        return movie