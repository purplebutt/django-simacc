from django import forms
from django.db.models import Q
from ..models import JRB, COA, CCF, JRE, BSG, COH


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
            self.add_error('amount', f"Invalid value: {ccval} should be a positive integer")
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

    # # custom validation for 'cashflow'
    # ccval = self.cleaned_data.get('cashflow') 
    # if ccval != None and ccval != '':
    #     if CCF.actives.filter(name=ccval).exists():
    #         self.cleaned_data['cashflow'] = CCF.actives.get(name=ccval)
    #     else:
    #         self.add_error('cashflow', f"No cash flow with name '{ccval}'") 
    #     if coa_instance and not coa_instance.is_cashflow: 
    #         self.add_error('cashflow', f"This field is no need, please provide a blank value.")
    # else:
    #     self.cleaned_data['cashflow'] = None
    #     if coa_instance and coa_instance.is_cashflow: 
    #         self.add_error('cashflow', f"This field is required.")

    # custom validation for 'busines seqment'
    ccval = self.cleaned_data.get('segment') 
    if ccval != None and ccval != '':
        if coa_instance and coa_instance.report() != 'PROFIT & LOSS': 
            self.add_error('segment', f"This field is no need, please provide a blank value.")
    else:
        self.cleaned_data['segment'] = None
        if coa_instance and coa_instance.report() == 'PROFIT & LOSS': 
            self.add_error('segment', f"This field is required.")
    # custom validation for 'cash flow'
    cashflow = self.cleaned_data.get('cashflow') 
    if cashflow != None and cashflow != "":
        if "|" in cashflow and cashflow[:1].isnumeric():
            number, name = cashflow.split("|")
            if CCF.actives.filter(Q(name=name)&Q(number=number)).exists():
                self.cleaned_data['cashflow'] = CCF.actives.get(number=float(number))
            else:
                self.add_error('cashflow', f"No cash flow with number & name '{cashflow}'") 
        else:
            if CCF.actives.filter(name=cashflow).exists():
                self.cleaned_data['cashflow'] = CCF.actives.get(name=cashflow)
            else:
                self.add_error('cashflow', f"No cash flow with name '{cashflow}'") 
    else:
        self.cleaned_data['cashflow'] = None
        if coa_instance and coa_instance.is_cashflow:
            self.add_error('cashflow', f"This field is required.")


class JRECreateSingleForm(forms.ModelForm):
    clean = jre_clean
    form_type = 'create'   # mark this form as create form
    date = forms.DateField()
    batch = forms.CharField()   # use datalist
    ref = forms.CharField()
    _form_info = forms.CharField(required=False, disabled=True,
        widget=forms.TextInput(attrs={'header':'Double entry form is better',
                                      'body':'Single entry form will record only one entry. We recommended you to use double entry form instead',
                                      'border_color':'border-danger',
                                      'color':'alert-danger',
                                      'footer':'Happy work :)',
                                      'footer_pos': 'float-end' })
    )
    description = forms.CharField(widget=forms.Textarea)
    group = forms.ChoiceField(choices=JRE._type, widget=forms.RadioSelect, label="Type")
    amount = forms.CharField(validators=[JRE.amount_validator], 
        widget=forms.TextInput(attrs={'class': 'border border-info border-3 create-amt'}))
    account = forms.CharField()     # use datalist
    segment = forms.ModelChoiceField(BSG.actives, required=False)
    cashflow = forms.CharField(required=False)    # use datalist
    pdf = forms.FileField(widget=forms.FileInput(attrs={'model':JRE}), required=False, label="Select PDF document")
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
        fields = ('date', 'batch', 'ref', '_form_info', 'description', 'group', 'amount', 'account', 'segment', 'cashflow', 'pdf', 'notes')


#! journal double entry
class JREUpdateForm(forms.ModelForm):
    clean = jre_clean
    form_type = 'double:update'   # mark this form as update form
    number = forms.CharField(disabled=True, label='Current Journal')   # use datalist
    pair = forms.CharField(disabled=True, required=False, label='Paired Journal')     # use datalist
    date = forms.DateField()
    batch = forms.CharField()   # use datalist
    ref = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    group = forms.ChoiceField(choices=JRE._type, widget=forms.RadioSelect, label="Type", help_text="Pair account will change accordingly")
    amount = forms.CharField(validators=[JRE.amount_validator], 
        widget=forms.TextInput(attrs={'class':'border border-info border-3 update-amt'}))
    account = forms.CharField()     # use datalist
    segment = forms.ModelChoiceField(BSG.actives, required=False)
    cashflow = forms.CharField(required=False)  # use datalist
    pdf = forms.FileField(widget=forms.FileInput(attrs={'model': 'jre'}), required=False, label="Change PDF document (old document will be deleted)")
    notes = forms.Textarea()
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 4
    pair.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRE', 'field':'number'}
    pair.col_width = 4
    date.col_width = 4
    batch.col_width = 6
    ref.col_width = 6
    description.col_width = 12
    group.col_width = 4
    amount.col_width = 4
    account.col_width = 8
    segment.col_width = 6
    cashflow.col_width = 6
    notes.col_width = 12
    batch.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRB', 'field':'number'}
    account.as_datalist = {'url':'accounting:utils_datalist', 'model':'COA'}
    cashflow.as_datalist = {'url':'accounting:utils_datalist', 'model':'CCF'}

    class Meta:
        model = JRE
        fields = ('number', 'pair', 'date', 'batch', 'ref', 'description', 'group', 'amount', 'account', 'segment', 'cashflow', 'pdf', 'notes')


class COAPair:
    __debit:COA=None
    __credit:COA=None

    @classmethod
    def set_debit(cls, coa:COA=None):
        if isinstance(coa, COA):
            cls.__debit=coa
        elif coa==None:
            cls.__credit=coa
        else:
            raise ValueError(f"{coa} should be an instance of COA")

    @classmethod
    def set_credit(cls, coa:COA=None):
        if isinstance(coa, COA):
            cls.__credit=coa
        elif coa==None:
            cls.__credit=coa
        else:
            raise ValueError(f"{coa} should be an instance of COA")

    @classmethod
    def get_debit(cls): return cls.__debit

    @classmethod
    def get_credit(cls): return cls.__credit

    @classmethod
    def exists(cls):
       return isinstance(cls.__debit, COA) or isinstance(cls.__credit, COA)

    @classmethod
    def is_cashflow(cls):
        checker = 0
        if hasattr(cls.__debit, 'is_cashflow'): checker += int(cls.__debit.is_cashflow)
        if hasattr(cls.__credit, 'is_cashflow'): checker += int(cls.__credit.is_cashflow)
        return checker > 0

    @classmethod
    def is_profit_and_loss(cls, report_key:str='pl'):
        checker = 0
        REPORT =  tuple(filter(lambda r: r[0]==report_key, COH._reports))[0][1]
        if hasattr(cls.__debit, 'report'): checker += int(cls.__debit.report()==REPORT)
        if hasattr(cls.__credit, 'report'): checker += int(cls.__credit.report()==REPORT)
        return checker > 0

def jre_double_entry_clean(self):
    # coa_instance should be put at the top of the code before the
    # calling on super().clean() method to make sure that super().clean()
    # method did not read the previous coa_instance value.
    coa_instance = COAPair()
    super(type(self), self).clean()     # make sure that others fields validation get fire
    # custom validation for 'batch'
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
            self.add_error('amount', f"Invalid value: {ccval} should be a positive integer")
    # custom validation for 'account debited'
    ccval = self.cleaned_data.get('account') 
    if ccval != None and ccval != "":
        if "|" in ccval and ccval[:1].isnumeric():
            number, name = ccval.split("|")
            if COA.actives.filter(Q(name=name)&Q(number=number)).exists():
                coa_instance.set_debit(COA.actives.get(number=number))
                self.cleaned_data['account'] = coa_instance.get_debit()
            else:
                self.add_error('account', f"No account with number & name '{ccval}'") 
        else:
            if COA.actives.filter(name=ccval).exists():
                coa_instance.set_debit(COA.actives.get(name=ccval))
                self.cleaned_data['account'] = coa_instance.get_debit()
            else:
                self.add_error('account', f"No account with name '{ccval}'") 
    # custom validation for 'account credited'
    ccval = self.cleaned_data.get('account2') 
    if ccval != None and ccval != "":
        if "|" in ccval and ccval[:1].isnumeric():
            number, name = ccval.split("|")
            if COA.actives.filter(Q(name=name)&Q(number=number)).exists():
                coa_instance.set_credit(COA.actives.get(number=number))
                self.cleaned_data['account2'] = coa_instance.get_credit()
            else:
                self.add_error('account2', f"No account with number & name '{ccval}'") 
        else:
            if COA.actives.filter(name=ccval).exists():
                coa_instance.set_credit(COA.actives.get(name=ccval))
                self.cleaned_data['account2'] = coa_instance.get_credit()
            else:
                self.add_error('account2', f"No account with name '{ccval}'") 

    # # custom validation for 'cashflow'
    # ccval = self.cleaned_data.get('cashflow') 
    # if ccval != None and ccval != '':
    #     if CCF.actives.filter(name=ccval).exists():
    #         self.cleaned_data['cashflow'] = CCF.actives.get(name=ccval)
    #     else:
    #         self.add_error('cashflow', f"No cash flow with name '{ccval}'") 
    #     if not coa_instance.is_cashflow(): 
    #         self.add_error('cashflow', f"This field is no need, please provide a blank value.")
    # else:
    #     self.cleaned_data['cashflow'] = None
    #     if coa_instance.is_cashflow(): 
    #         self.add_error('cashflow', f"This field is required.")

    # custom validation for 'busines seqment'
    ccval = self.cleaned_data.get('segment') 
    if ccval != None and ccval != '':
        if not coa_instance.is_profit_and_loss(): 
            self.add_error('segment', f"This field is no need, please provide a blank value.")
    else:
        self.cleaned_data['segment'] = None
        if coa_instance.is_profit_and_loss(): 
            self.add_error('segment', f"This field is required.")
    # custom validation for 'cash flow'
    cashflow = self.cleaned_data.get('cashflow') 
    if cashflow != None and cashflow != "":
        if "|" in cashflow and cashflow[:1].isnumeric():
            number, name = cashflow.split("|")
            if CCF.actives.filter(Q(name=name)&Q(number=number)).exists():
                self.cleaned_data['cashflow'] = CCF.actives.get(number=float(number))
            else:
                self.add_error('cashflow', f"No cash flow with number & name '{cashflow}'") 
        else:
            if CCF.actives.filter(name=cashflow).exists():
                self.cleaned_data['cashflow'] = CCF.actives.get(name=cashflow)
            else:
                self.add_error('cashflow', f"No cash flow with name '{cashflow}'") 
    else:
        self.cleaned_data['cashflow'] = None
        if coa_instance and coa_instance.is_cashflow:
            self.add_error('cashflow', f"This field is required.")


class JRECreateForm(forms.ModelForm):
    clean = jre_double_entry_clean
    form_type = 'double:create'   # mark this form as create form
    date = forms.DateField()
    batch = forms.CharField()   # use datalist
    ref = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    account = forms.CharField(label='Account debited', widget=forms.TextInput(attrs={'class':'bg-secondary'}))     # use datalist
    account2 = forms.CharField(label='Account credited')     # use datalist
    amount = forms.CharField(validators=[JRE.amount_validator], help_text="Provide a positive integer", 
        widget=forms.TextInput(attrs={'class':'border border-info border-3 create-amt'}))
    segment = forms.ModelChoiceField(BSG.actives, required=False)
    cashflow = forms.CharField(required=False)    # use datalist
    pdf = forms.FileField(widget=forms.FileInput(), required=False, label="Select PDF document")
    notes = forms.CharField(widget=forms.Textarea, required=False)
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    date.col_width = 4
    batch.col_width = 4
    ref.col_width = 4
    description.col_width = 12
    account.col_width = 6
    account2.col_width = 6
    amount.col_width = 3
    segment.col_width = 4
    cashflow.col_width = 5
    notes.col_width = 12
    batch.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRB'}
    account.as_datalist = {'url':'accounting:utils_datalist', 'model':'COA'}
    account2.as_datalist = {'url':'accounting:utils_datalist', 'model':'COA'}
    cashflow.as_datalist = {'url':'accounting:utils_datalist', 'model':'CCF'}

    class Meta:
        model = JRE
        fields = ('date', 'batch', 'ref', 'description', 'account', 'account2', 'amount', 'segment', 'cashflow', 'pdf', 'notes')
