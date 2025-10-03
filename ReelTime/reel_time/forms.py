from django import forms

class RegisterForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    username = forms.CharField(max_length=150, label="Username")
