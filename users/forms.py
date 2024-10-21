from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import Profile



class UserRegisterForm(UserCreationForm):
#    phone_regex = RegexValidator(
 #   regex=r'^\+?1?\d{9,15}$', 
  #  message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
   # )
    #phone_number = forms.CharField(validators=[phone_regex], max_length=17, required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']



class UserUpdateForm(forms.ModelForm):
    #phone_regex = RegexValidator(
    #regex=r'^\+?1?\d{9,15}$', 
    #message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    #)
   # phone_number = forms.CharField(validators=[phone_regex], max_length=17, required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']