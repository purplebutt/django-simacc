from django import forms
from ..models import COA, COH


#! chart of account forms
class COACreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField()
    name = forms.CharField()
    normal = forms.ChoiceField(choices=COA._normal_balance, widget=forms.RadioSelect)
    header = forms.ModelChoiceField(COH.objects)
    notes = forms.CharField(widget=forms.Textarea(attrs={'style':'height:120px'}), required=False)
    is_cashflow = forms.CharField(widget=forms.CheckboxInput(), label_suffix="")
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 4
    header.col_width = 8
    name.col_width = 12
    normal.col_width = 3

    class Meta:
        model = COA
        fields = ('number', 'header', 'name', 'normal', 'notes', 'is_cashflow')

class COAUpdateForm(forms.ModelForm):
    form_type = 'update'   # mark this form as update form
    number = forms.CharField()
    name = forms.CharField()
    normal = forms.ChoiceField(choices=COA._normal_balance, widget=forms.RadioSelect)
    header = forms.ModelChoiceField(COH.objects)
    notes = forms.CharField(widget=forms.Textarea(attrs={'style':'height:120px'}), required=False)
    is_cashflow = forms.CharField(widget=forms.CheckboxInput(), label_suffix="")
    is_active = forms.CharField(widget=forms.CheckboxInput(), label_suffix="")
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 4
    header.col_width = 8
    name.col_width = 12
    normal.col_width = 3

    class Meta:
        model = COA
        fields = ('number', 'header', 'name', 'normal', 'notes', 'is_cashflow', 'is_active')

