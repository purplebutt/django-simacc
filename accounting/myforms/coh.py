from django import forms
from ..models import COH

#! chart of account header forms
class COHCreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField()
    name = forms.CharField()
    report = forms.ChoiceField(choices=COH._reports)
    group = forms.ChoiceField(choices=COH._account_group)
    notes = forms.CharField(widget=forms.Textarea(attrs={'style':'height:120px'}), required=False)
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 3
    report.col_width = 4
    group.col_width = 5
    name.col_width = 12

    class Meta:
        model = COH
        fields = ('number', 'report', 'group', 'name', 'notes')

class COHUpdateForm(forms.ModelForm):
    form_type = 'update'   # mark this form as update form
    number = forms.CharField()
    name = forms.CharField()
    report = forms.ChoiceField(choices=COH._reports)
    group = forms.ChoiceField(choices=COH._account_group)
    notes = forms.CharField(widget=forms.Textarea(attrs={'style':'height:120px'}), required=False)
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 3
    report.col_width = 4
    group.col_width = 5
    name.col_width = 12

    class Meta:
        model = COH
        fields = ('number', 'report', 'group', 'name', 'notes')

