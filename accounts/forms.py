from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    first_name.col_width = 4
    last_name.col_width = 4

    class Meta:
        model = User
        fields = ('first_name', 'last_name', )

class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(required=False, widget=forms.NumberInput())
    address = forms.CharField(required=False, widget=forms.Textarea())
    dob = forms.DateTimeField(required=False, widget=forms.DateInput())
    gender = forms.ChoiceField(choices=Profile._gender, required=False)
    city = forms.CharField(required=False)
    job = forms.CharField(required=False)

    gender.col_width = 4
    city.col_width = 6
    phone.col_width = 6
    job.col_width = 6
    dob.col_width = 6

    class Meta:
        model = Profile
        fields = ('gender', 'address', 'city', 'phone', 'job', 'dob',)

class ProfileImageForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput())
    class Meta:
        model = Profile
        fields = ('image',)
