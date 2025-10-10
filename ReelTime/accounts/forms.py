from django import forms
from accounts.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        for field in ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']:
            if not cleaned_data.get(field):
                self.add_error(field, "This field is required.")
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise ValidationError("Passwords do not match")
        cleaned_data['password'] = make_password(password)  # hash password
        return cleaned_data
