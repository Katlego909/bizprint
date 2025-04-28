from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile, NewsletterSubscriber

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    full_name = forms.CharField(label="Full Name")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone', 'address', 'city', 'postal_code']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'e.g. 12345'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class NewsletterSignupForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'newsletter-input'
            })
        }