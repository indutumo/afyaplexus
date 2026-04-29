from django import forms
from .models import Hospital

class HospitalForm(forms.ModelForm):

    CENTRE_CHOICES = [
        ('Government', 'Government'),
        ('Private', 'Private'),
        ('Faith Based', 'Faith Based'),
    ]

    centre_type = forms.ChoiceField(
        choices=CENTRE_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full border p-2 rounded'})
    )

    class Meta:
        model = Hospital
        fields = [
            'name', 'mobile_number', 'alternative_number',
            'email_address', 'website', 'centre_type',
            'location', 'google_pin', 'description',
            'county', 'constituent', 'ward',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border p-2 rounded'}),
            'mobile_number': forms.TextInput(attrs={'class': 'w-full border p-2 rounded'}),
            'alternative_number': forms.TextInput(attrs={'class': 'w-full border p-2 rounded'}),
            'email_address': forms.EmailInput(attrs={'class': 'w-full border p-2 rounded'}),
            'website': forms.URLInput(attrs={'class': 'w-full border p-2 rounded'}),
            'location': forms.TextInput(attrs={'class': 'w-full border p-2 rounded'}),
            'centre_type': forms.Select(attrs={'class': 'w-full border p-2 rounded'}),
            'county': forms.Select(attrs={'class': 'w-full border p-2 rounded'}),
            'constituent': forms.Select(attrs={'class': 'w-full border p-2 rounded'}),
            'ward': forms.Select(attrs={'class': 'w-full border p-2 rounded'}),
            'google_pin': forms.TextInput(attrs={'class': 'w-full border p-2 rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full border p-2 rounded'}),
        }