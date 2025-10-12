from django import forms
from accounts.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import re


class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm your password'}), 
        required=True
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your last name'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Create a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Enter your email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your phone number'}),
            'password': forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Create a password'}),
        }

    # ✅ Validate username uniqueness
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        
        return username

    # ✅ Validate phone number
    def clean_phone_number(self):   
        phone = self.cleaned_data.get('phone_number', '').replace(' ', '')
        original_phone = self.data.get('phone_number', '')
        if not phone.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        if len(phone) != 11:
            raise ValidationError("Phone number must be exactly 11 digits long.")
        return original_phone

    # ✅ Validate password strength
    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not password:
            raise ValidationError("Password is required.")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r"[@$!%*?&-]", password):
            raise ValidationError("Password must contain at least one special character (@, $, !, %, *, ?, &, -).")

        return password

    # ✅ Cross-field validation
    def clean(self):
        cleaned_data = super().clean()

        # Check all required fields
        for field in ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']:
            if not cleaned_data.get(field):
                self.add_error(field, "This field is required.")

        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            raise ValidationError("Passwords do not match.")

        # Hash password before saving to DB
        if password:
            cleaned_data['password'] = make_password(password)

        return cleaned_data
