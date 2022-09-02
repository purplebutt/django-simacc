from django import forms
from ..models import CCF


#! chart of cash flow forms 
class CCFCreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField()
    name = forms.CharField()
    flow = forms.ChoiceField(choices=CCF._flow, widget=forms.RadioSelect)
    activity = forms.ChoiceField(choices=CCF._activities)
    notes = forms.CharField(widget=forms.Textarea(attrs={'style':'height:120px'}), required=False)
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 3
    name.col_width = 9
    flow.col_width = 5
    activity.col_width = 7

    class Meta:
        model = CCF
        fields = ('number', 'name', 'flow', 'activity', 'notes')

class CCFUpdateForm(forms.ModelForm):
    form_type = 'update'   # mark this form as update form
    number = forms.CharField()
    name = forms.CharField()
    flow = forms.ChoiceField(choices=CCF._flow, widget=forms.RadioSelect)
    activity = forms.ChoiceField(choices=CCF._activities)
    notes = forms.CharField(widget=forms.Textarea(attrs={'style':'height:120px'}), required=False)
    is_active = forms.CharField(widget=forms.CheckboxInput(), label_suffix="")
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 3
    name.col_width = 9
    flow.col_width = 5
    activity.col_width = 6

    class Meta:
        model = CCF
        fields = ('number', 'name', 'flow', 'activity', 'notes', 'is_active')

