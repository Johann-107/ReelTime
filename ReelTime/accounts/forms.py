from django import forms
from accounts.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import re
import cloudinary.uploader

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

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].required = False
        self.fields['profile_picture'].help_text = "Upload a profile picture (JPG, PNG only, max 2MB)"

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        
        if profile_picture:
            # Check if it's a new upload (has size attribute) or existing Cloudinary resource
            if hasattr(profile_picture, 'size'):
                # Validate file size (max 2MB for profile pictures)
                if profile_picture.size > 2 * 1024 * 1024:
                    raise forms.ValidationError("Profile picture too large ( > 2MB )")
                
                # Validate file type
                valid_extensions = ['jpg', 'jpeg', 'png']
                extension = profile_picture.name.split('.')[-1].lower()
                if extension not in valid_extensions:
                    raise forms.ValidationError("Unsupported file extension. Only JPG and PNG are allowed.")
        
        return profile_picture

    def clean_username(self):
        username = self.cleaned_data['username']
        if not self.instance.is_admin and ' ' in username:
            raise forms.ValidationError("Username cannot contain spaces.")
        return username