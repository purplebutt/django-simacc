from django import forms
from django.db.models import Q
from ..models import JRB, COA, CCF, JRE, BSG


#! journal single entry
def jre_clean(self):
    super(type(self), self).clean()     # make sure that others fields validation get fire
    # custom validation for 'batch'
    coa_instance = None
    ccval = self.cleaned_data.get('batch') 
    if ccval is not None:
        if JRB.actives.filter(number=ccval).exists():
            self.cleaned_data['batch'] = JRB.actives.get(number=ccval)
        else:
            self.add_error('batch', f"No batch with number '{ccval}'") 
    # custom validation for 'amount'
    ccval = self.cleaned_data.get('amount')
    if ccval is not None:
        ccval = ccval.replace(",", "")
        if ccval.isnumeric() and int(ccval) > 0:
            self.cleaned_data['amount'] = ccval
        else:
            self.add_error('amount', f"Invalid value: {value} should be a positive integer")
    # custom validation for 'account'
    ccval = self.cleaned_data.get('account') 
    if ccval is not None:
        if "|" in ccval and ccval[:1].isnumeric():
            number, name = ccval.split("|")
            if COA.actives.filter(Q(name=name)&Q(number=number)).exists():
                coa_instance = COA.actives.get(number=number)
                self.cleaned_data['account'] = coa_instance
            else:
                self.add_error('account', f"No account with number & name '{ccval}'") 
        else:
            if COA.actives.filter(name=ccval).exists():
                coa_instance = COA.actives.get(name=ccval)
                self.cleaned_data['account'] = coa_instance
            else:
                self.add_error('account', f"No account with name '{ccval}'") 
    # custom validation for 'cashflow'
    ccval = self.cleaned_data.get('cashflow') 
    if ccval != None and ccval != '':
        if CCF.actives.filter(name=ccval).exists():
            self.cleaned_data['cashflow'] = CCF.actives.get(name=ccval)
        else:
            self.add_error('cashflow', f"No cash flow with name '{ccval}'") 
        if coa_instance and not coa_instance.is_cashflow: 
            self.add_error('cashflow', f"This field is no need, please provide a blank value.")
    else:
        self.cleaned_data['cashflow'] = None
        if coa_instance and coa_instance.is_cashflow: 
            self.add_error('cashflow', f"This field is required.")
    # custom validation for 'busines seqment'
    ccval = self.cleaned_data.get('segment') 
    if ccval != None and ccval != '':
        if coa_instance and coa_instance.report() != 'PROFIT & LOSS': 
            self.add_error('segment', f"This field is no need, please provide a blank value.")
    else:
        self.cleaned_data['segment'] = None
        if coa_instance and coa_instance.report() == 'PROFIT & LOSS': 
            self.add_error('segment', f"This field is required.")

class JRECreateSingleForm(forms.ModelForm):
    clean = jre_clean
    form_type = 'create'   # mark this form as create form
    date = forms.DateField()
    batch = forms.CharField()   # use datalist
    ref = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    group = forms.ChoiceField(choices=JRE._type, widget=forms.RadioSelect, label="Type")
    amount = forms.CharField(validators=[JRE.amount_validator], widget=forms.TextInput(attrs={'class': 'border border-info border-3'}))
    account = forms.CharField()     # use datalist
    segment = forms.ModelChoiceField(BSG.actives, required=False)
    cashflow = forms.CharField(required=False)    # use datalist
    notes = forms.Textarea()
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    date.col_width = 4
    batch.col_width = 4
    ref.col_width = 4
    description.col_width = 12
    group.col_width = 12
    amount.col_width = 5
    account.col_width = 7
    segment.col_width = 5
    cashflow.col_width = 7
    notes.col_width = 12
    batch.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRB'}
    account.as_datalist = {'url':'accounting:utils_datalist', 'model':'COA'}
    cashflow.as_datalist = {'url':'accounting:utils_datalist', 'model':'CCF'}

    class Meta:
        model = JRE
        fields = ('date', 'batch', 'ref', 'description', 'group', 'amount', 'account', 'segment', 'cashflow', 'notes')
