from django import forms
from .models import Movie, MovieAdminDetails
from django.forms.widgets import DateInput, Textarea

class MovieAdminDetailsForm(forms.ModelForm):
    class Meta:
        model = MovieAdminDetails
        fields = ['release_date', 'end_date', 'showing_times', 'poster']
        widgets = {
            'release_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
            'showing_times': Textarea(attrs={'rows': 2, 'placeholder': 'e.g. ["10:00 AM", "1:30 PM", "6:45 PM"]'}),
        }

class MovieForm(forms.ModelForm):
    # Embed the admin details form fields here:
    release_date = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    showing_times = forms.CharField(
        widget=Textarea(attrs={'rows': 2, 'placeholder': 'e.g. [{"time": "10:00 AM", "max_seats": 100}, {"time": "1:30 PM", "max_seats": 120}]'}),
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
        # Optionally receive admin user to save later
        self.admin = kwargs.pop('admin', None)
        super().__init__(*args, **kwargs)

        # If editing existing movie and admin details, populate initial admin fields
        if self.instance.pk and self.admin:
            try:
                admin_details = self.instance.admin_details.get(admin=self.admin)
                self.fields['release_date'].initial = admin_details.release_date
                self.fields['end_date'].initial = admin_details.end_date
                self.fields['showing_times'].initial = admin_details.showing_times
                self.fields['poster'].initial = admin_details.poster
            except MovieAdminDetails.DoesNotExist:
                pass

    def clean_showing_times(self):
        data = self.cleaned_data['showing_times']
        if isinstance(data, str):
            import json
            try:
                data_list = json.loads(data)
                if not isinstance(data_list, list):
                    raise forms.ValidationError("Showing times must be a list.")
                # Ensure each dict has "time" and "max_seats"
                for i, s in enumerate(data_list):
                    if 'time' not in s:
                        raise forms.ValidationError(f'Showtime at index {i} must have a "time" field.')
                    if 'max_seats' not in s or s['max_seats'] in [None, ""]:
                        s['max_seats'] = 50  # default seats if not provided
                return data_list
            except Exception:
                raise forms.ValidationError(
                    'Enter showing times as a JSON list, e.g. [{"time": "10:00 AM", "max_seats": 100}]'
                )
        return data

    def save(self, commit=True):
        movie = super().save(commit=commit)

        if self.admin:
            # Ensure showing_times is a list of dicts with 'time' and 'max_seats'
            showing_times = self.cleaned_data.get('showing_times', [])
            for s in showing_times:
                if 'time' not in s:
                    continue  # skip invalid entries
                if 'max_seats' not in s or s['max_seats'] in [None, ""]:
                    s['max_seats'] = 50  # default seats if not provided

            # Save or create admin details
            admin_details, created = MovieAdminDetails.objects.get_or_create(
                movie=movie,
                admin=self.admin,
                defaults={
                    'release_date': self.cleaned_data['release_date'],
                    'end_date': self.cleaned_data['end_date'],
                    'showing_times': showing_times,
                    'poster': self.cleaned_data.get('poster'),
                }
            )

            if not created:
                # Update existing admin details
                admin_details.release_date = self.cleaned_data['release_date']
                admin_details.end_date = self.cleaned_data['end_date']
                admin_details.showing_times = showing_times
                if self.cleaned_data.get('poster'):
                    admin_details.poster = self.cleaned_data['poster']
                admin_details.save()

        return movie
