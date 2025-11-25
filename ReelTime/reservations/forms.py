# reservations/forms.py
from django import forms
from .models import Reservation

class ReservationEditForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['number_of_seats', 'selected_seats']
        widgets = {
            'number_of_seats': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'selected_seats': forms.HiddenInput()  # We'll handle this with JavaScript
        }
    
    def clean_number_of_seats(self):
        number_of_seats = self.cleaned_data['number_of_seats']
        if number_of_seats < 1:
            raise forms.ValidationError("Number of seats must be at least 1.")
        if number_of_seats > 10:
            raise forms.ValidationError("Cannot reserve more than 10 seats.")
        return number_of_seats