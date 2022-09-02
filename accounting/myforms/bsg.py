from django import forms
from ..models import BSG


#! business seqment forms 
class BSGCreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField()
    group = forms.CharField(label='Type')
    name = forms.CharField(label='Business Name')
    notes = forms.CharField(widget=forms.Textarea(attrs={'style':'height:150px'}), required=False)
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 4
    group.col_width = 8
    name.col_width = 12
    group.as_datalist = {'url':'accounting:utils_datalist', 'model':'BSG', 'query':'?field=group'}

    class Meta:
        model = BSG
        fields = ('number', 'group', 'name', 'notes')

class BSGUpdateForm(forms.ModelForm):
    form_type = 'update'   # mark this form as update form
    number = forms.CharField()
    group = forms.CharField(label='Type')
    name = forms.CharField(label='Business Name')
    notes = forms.CharField(widget=forms.Textarea(attrs={'style':'height:150px'}), required=False)
    is_active = forms.CharField(widget=forms.CheckboxInput(), label_suffix="")
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 4
    group.col_width = 8
    name.col_width = 12
    group.as_datalist = {'url':'accounting:utils_datalist', 'model':'BSG', 'query':'?field=group'}

    class Meta:
        model = BSG
        fields = ('number', 'group', 'name', 'notes', 'is_active')

