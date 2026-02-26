from django import forms
from django.contrib.auth.models import User
from .models import UserAddress, UserProfile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control premium-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control premium-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control premium-input', 'readonly': 'readonly'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'bio', 'phone', 'date_of_birth']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control premium-input', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control premium-input'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control premium-input', 'type': 'date'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control premium-input'}),
        }

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['full_name', 'phone', 'street_address', 'city', 'state', 'zip_code', 'is_default']
        widgets = {
            'street_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control premium-input'})
        self.fields['is_default'].widget.attrs.update({'class': 'form-check-input'})