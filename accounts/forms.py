from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(disabled=True, widget=forms.TextInput(attrs={'title':'Email can not be changed', 'readonly':'true'}))

    first_name.col_width = 6
    last_name.col_width = 6
    email.col_width = 5

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileUpdateForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=Profile._gender, required=False)
    phone = forms.CharField(required=False, widget=forms.NumberInput())
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'height:90px'}))
    job = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'height:90px'}))
    city = forms.CharField(required=False)
    dob = forms.DateTimeField(required=False, widget=forms.DateInput())

    gender.col_width = 3
    phone.col_width = 4
    address.col_width = 7
    job.col_width = 5
    city.col_width = 8
    dob.col_width = 4

    class Meta:
        model = Profile
        fields = ('gender', 'phone', 'address', 'job', 'city', 'dob')

class ProfileImageForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput())
    class Meta:
        model = Profile
        fields = ('image',)
