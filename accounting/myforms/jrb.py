from django import forms
from ..models import JRB


#! journal batch forms 
class JRBCreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField(validators=[JRB.number_validator], label='Code')
    group = forms.CharField(label="Type")
    description = forms.CharField(widget=forms.Textarea(attrs={'style':'height:150px'}))
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 5
    group.col_width = 7
    description.col_width = 12
    group.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRB', 'query':'?field=group'}

    class Meta:
        model = JRB
        fields = ('number', 'group', 'description')

class JRBUpdateForm(forms.ModelForm):
    form_type = 'update'   # mark this form as update form
    number = forms.CharField(label='Code')
    group = forms.CharField(label="Type")
    description = forms.CharField(widget=forms.Textarea(attrs={'style':'height:150px'}))
    is_active = forms.CharField(widget=forms.CheckboxInput(), label_suffix="")
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 5
    group.col_width = 7
    description.col_width = 12
    group.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRB', 'query':'?field=group'}

    class Meta:
        model = JRB
        fields = ('number', 'group', 'description', 'is_active')

