from django import forms
from .models import Doctor

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'title',
            'name',
            'mobile_number',
            'alternative_number',
            'email_address',
            'location',
            'license_number',
            'license',
            'hospital',
            'profile_picture'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'mobile_number': forms.TextInput(attrs={'class': 'input'}),
            'alternative_number': forms.TextInput(attrs={'class': 'input'}),
            'email_address': forms.EmailInput(attrs={'class': 'input'}),
            'location': forms.TextInput(attrs={'class': 'input'}),
            'license_number': forms.TextInput(attrs={'class': 'input'}),
            'hospital': forms.TextInput(attrs={'class': 'input'}),
        }