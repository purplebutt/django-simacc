from django import forms
from ..models import Company
from django.contrib.auth.models import User, Group


class CompanyEditForm(forms.ModelForm):
    name = forms.CharField(widget=forms.Textarea(attrs={'style':'height:70px;'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'style':'height:70px;'}))
    number = forms.CharField()
    legal = forms.ChoiceField(choices=Company._legal)
    business_type = forms.CharField()
    city = forms.CharField()
    country = forms.CharField()
    phone = forms.CharField()
    email = forms.EmailField()
    desc = forms.CharField(widget=forms.Textarea(attrs={'style':'height:60px'}), required=False)

    name.col_width = 6
    address.col_width = 6
    number.col_width = 4
    legal.col_width = 4
    business_type.col_width = 4
    business_type.as_datalist = {'url':'accounting:utils_datalist', 'model':'Company', 'query':'?field=business_type'}
    city.col_width = 3
    city.as_datalist = {'url':'accounting:utils_datalist', 'model':'Company', 'query':'?field=city'}
    country.col_width = 3
    country.as_datalist = {'url':'accounting:utils_datalist', 'model':'Company', 'query':'?field=country&upper=1'}
    phone.col_width = 3
    email.col_width = 3
    desc.col_width = 12

    class Meta:
        model = Company
        fields = ('name', 'address', 'number', 'legal', 'business_type', 'city', 'country', 'phone', 'email', 'desc')


class ConfigEditForm(forms.Form):
    closed_period = forms.DateField(help_text="Accounting period will be close to this date", label="Close period", required=False)
    current_period_start = forms.DateField(label="Current period start date", required=False)
    current_period_end = forms.DateField(label="Current period end date", required=False)

    class Meta:
        fields = ('closed_period', 'current_period')


class UserEditGroupForm(forms.ModelForm):
    username = forms.CharField(disabled=True)
    first_name = forms.CharField(disabled=True)
    last_name = forms.CharField(disabled=True)
    groups = forms.ModelMultipleChoiceField(Group.objects, widget=forms.SelectMultiple(attrs={'style':'height:130px'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'groups')