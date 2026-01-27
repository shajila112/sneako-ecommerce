from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    full_name=forms.CharField(max_length=100,required=True)
    email=forms.EmailField(required=True)

    class Meta:
        model=User
        fields=('full_name','email','password1','password2')

    def save(self,commit=True):
        user=super().save(commit=False)
        user.email=self.cleaned_data['email']

        full_name=self.cleaned_data['full_name']
        if " " in full_name:
            user.first_name,user.last_name=full_name.split(" ",1)
        else:
            user.first_name=full_name


        if commit:
            user.save()
        return user
               