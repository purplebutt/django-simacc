from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import *


#! company forms
class CompanyCreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    name = forms.CharField()
    email = forms.CharField(required=False, widget=forms.EmailInput())
    address = forms.CharField(widget=forms.Textarea())

    name.col_width = 6
    email.col_width = 6

    class Meta:
        model = Company
        fields = ('name', 'email', 'address')

class CompanyUpdateForm(forms.ModelForm):
    form_type = 'update'   # mark this form as update form
    name = forms.CharField()
    phone = forms.CharField(required=False)
    email = forms.CharField(required=False, widget=forms.EmailInput())
    address = forms.CharField(widget=forms.Textarea())
    legal = forms.ChoiceField(choices=Company._legal)
    business_type = forms.CharField(required=False)
    city = forms.CharField(required=False)
    country = forms.CharField(required=False)

    name.col_width = 6
    phone.col_width = 3
    email.col_width = 3
    legal.col_width = 3
    business_type.col_width = 9
    city.col_width = 8
    country.col_width = 4

    class Meta:
        model = Company
        fields = ('name', 'phone', 'email', 'address', 'legal', 'business_type', 'city', 'country')


#! chart of account header forms
class COHCreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField()
    name = forms.CharField()
    report = forms.ChoiceField(choices=COH._reports)
    group = forms.ChoiceField(choices=COH._account_group)
    notes = forms.CharField(widget=forms.Textarea(), required=False)
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
    notes = forms.CharField(widget=forms.Textarea(), required=False)
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 3
    report.col_width = 4
    group.col_width = 5
    name.col_width = 12

    class Meta:
        model = COH
        fields = ('number', 'report', 'group', 'name', 'notes')


#! chart of account forms
class COACreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField()
    name = forms.CharField()
    normal = forms.ChoiceField(choices=COA._normal_balance, widget=forms.RadioSelect)
    header = forms.ModelChoiceField(COH.objects)
    notes = forms.CharField(widget=forms.Textarea(), required=False)
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
    notes = forms.CharField(widget=forms.Textarea(), required=False)
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


#! chart of cash flow forms 
class CCFCreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField()
    name = forms.CharField()
    flow = forms.ChoiceField(choices=CCF._flow, widget=forms.RadioSelect)
    activity = forms.ChoiceField(choices=CCF._activities)
    notes = forms.CharField(widget=forms.Textarea(), required=False)
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
    notes = forms.CharField(widget=forms.Textarea(), required=False)
    is_active = forms.CharField(widget=forms.CheckboxInput(), label_suffix="")
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 3
    name.col_width = 9
    flow.col_width = 5
    activity.col_width = 6

    class Meta:
        model = CCF
        fields = ('number', 'name', 'flow', 'activity', 'notes', 'is_active')


#! business seqment forms 
class BSGCreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField()
    name = forms.CharField(label='Business Name')
    group = forms.CharField()
    notes = forms.CharField(widget=forms.Textarea(), required=False)
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 3
    name.col_width = 9
    group.col_width = 7
    group.as_datalist = {'url':'accounting:utils_datalist', 'model':'BSG', 'query':'?field=group'}

    class Meta:
        model = BSG
        fields = ('number', 'name', 'group', 'notes')

class BSGUpdateForm(forms.ModelForm):
    form_type = 'update'   # mark this form as update form
    number = forms.CharField()
    name = forms.CharField(label='Business Name')
    group = forms.CharField()
    notes = forms.CharField(widget=forms.Textarea(), required=False)
    is_active = forms.CharField(widget=forms.CheckboxInput(), label_suffix="")
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 3
    name.col_width = 9
    group.col_width = 7
    group.as_datalist = {'url':'accounting:utils_datalist', 'model':'BSG', 'query':'?field=group'}

    class Meta:
        model = BSG
        fields = ('number', 'name', 'group', 'notes', 'is_active')


#! journal batch forms 
class JRBCreateForm(forms.ModelForm):
    form_type = 'create'   # mark this form as create form
    number = forms.CharField(validators=[JRB.number_validator])
    group = forms.CharField(label="Type")
    description = forms.Textarea()
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
    number = forms.CharField()
    group = forms.CharField(label="Type")
    description = forms.Textarea()
    is_active = forms.CharField(widget=forms.CheckboxInput(), label_suffix="")
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    number.col_width = 5
    group.col_width = 7
    description.col_width = 12
    group.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRB', 'query':'?field=group'}

    class Meta:
        model = JRB
        fields = ('number', 'group', 'description', 'is_active')


#! journal entry
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

class JRECreateForm_bak(forms.ModelForm):
    clean = jre_clean
    form_type = 'create'   # mark this form as create form
    date = forms.DateField()
    batch = forms.CharField()   # use datalist
    ref = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    group = forms.ChoiceField(choices=JRE._type, widget=forms.RadioSelect, label="Type")
    amount = forms.CharField(validators=[JRE.amount_validator])
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

class JREUpdateForm(forms.ModelForm):
    clean = jre_clean
    form_type = 'update'   # mark this form as update form
    date = forms.DateField()
    number = forms.CharField(disabled=True)   # use datalist
    batch = forms.CharField()   # use datalist
    ref = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    group = forms.ChoiceField(choices=JRE._type, widget=forms.RadioSelect, label="Type")
    amount = forms.CharField(validators=[JRE.amount_validator])
    account = forms.CharField()     # use datalist
    segment = forms.ModelChoiceField(BSG.actives, required=False)
    cashflow = forms.CharField(required=False)  # use datalist
    notes = forms.Textarea()
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    date.col_width = 3
    batch.col_width = 3
    ref.col_width = 3
    number.col_width = 3
    description.col_width = 12
    group.col_width = 4
    amount.col_width = 5
    account.col_width = 7
    segment.col_width = 6
    cashflow.col_width = 6
    notes.col_width = 12
    batch.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRB', 'field':'number'}
    account.as_datalist = {'url':'accounting:utils_datalist', 'model':'COA'}
    cashflow.as_datalist = {'url':'accounting:utils_datalist', 'model':'CCF'}

    class Meta:
        model = JRE
        fields = ('date', 'batch', 'ref', 'number', 'description', 'group', 'amount', 'account', 'segment', 'cashflow', 'notes')

#! journal double entry
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
            self.add_error('amount', f"Invalid value: {value} should be a positive integer")
    # custom validation for 'account debited'
    ccval = self.cleaned_data.get('account') 
    if ccval is not None and ccval is not "":
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
    if ccval is not None and ccval is not "":
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
    # custom validation for 'cashflow'
    ccval = self.cleaned_data.get('cashflow') 
    if ccval != None and ccval != '':
        if CCF.actives.filter(name=ccval).exists():
            self.cleaned_data['cashflow'] = CCF.actives.get(name=ccval)
        else:
            self.add_error('cashflow', f"No cash flow with name '{ccval}'") 
        if not coa_instance.is_cashflow(): 
            self.add_error('cashflow', f"This field is no need, please provide a blank value.")
    else:
        self.cleaned_data['cashflow'] = None
        if coa_instance.is_cashflow(): 
            self.add_error('cashflow', f"This field is required.")
    # custom validation for 'busines seqment'
    ccval = self.cleaned_data.get('segment') 
    if ccval != None and ccval != '':
        if not coa_instance.is_profit_and_loss(): 
            self.add_error('segment', f"This field is no need, please provide a blank value.")
    else:
        self.cleaned_data['segment'] = None
        if coa_instance.is_profit_and_loss(): 
            self.add_error('segment', f"This field is required.")

class JRECreateForm(forms.ModelForm):
    clean = jre_double_entry_clean
    form_type = 'double:create'   # mark this form as create form
    date = forms.DateField()
    batch = forms.CharField()   # use datalist
    ref = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    amount = forms.CharField(validators=[JRE.amount_validator], help_text="Provide a positive integer")
    account = forms.CharField(label='Account debited')     # use datalist
    account2 = forms.CharField(label='Account credited')     # use datalist
    segment = forms.ModelChoiceField(BSG.actives, required=False)
    cashflow = forms.CharField(required=False)    # use datalist
    notes = forms.CharField(widget=forms.Textarea, required=False)
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    date.col_width = 4
    batch.col_width = 4
    ref.col_width = 4
    description.col_width = 7
    amount.col_width = 5
    account.col_width = 6
    account2.col_width = 6
    segment.col_width = 5
    cashflow.col_width = 7
    notes.col_width = 12
    batch.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRB'}
    account.as_datalist = {'url':'accounting:utils_datalist', 'model':'COA'}
    account2.as_datalist = {'url':'accounting:utils_datalist', 'model':'COA'}
    cashflow.as_datalist = {'url':'accounting:utils_datalist', 'model':'CCF'}

    class Meta:
        model = JRE
        fields = ('date', 'batch', 'ref', 'description', 'amount', 'account', 'account2', 'segment', 'cashflow', 'notes')

class JREUpdateForm_bak(forms.ModelForm):
    clean = jre_double_entry_clean
    form_type = 'double:update'   # mark this form as create form
    date = forms.DateField()
    batch = forms.CharField()   # use datalist
    ref = forms.CharField()
    number = forms.CharField(disabled=True)   # use datalist
    description = forms.CharField(widget=forms.Textarea)
    amount = forms.CharField(validators=[JRE.amount_validator], help_text="Provide a positive integer")
    account = forms.CharField(label='Account debited')     # use datalist
    account2 = forms.CharField(label='Account credited')     # use datalist
    segment = forms.ModelChoiceField(BSG.actives, required=False)
    cashflow = forms.CharField(required=False)    # use datalist
    notes = forms.CharField(widget=forms.Textarea, required=False)
    no_password = True  # prevent password hide/show javascript to load (form without password field)

    date.col_width = 3
    batch.col_width = 3
    ref.col_width = 3
    number.col_width = 3
    description.col_width = 7
    amount.col_width = 5
    account.col_width = 6
    account2.col_width = 6
    segment.col_width = 5
    cashflow.col_width = 7
    notes.col_width = 12
    batch.as_datalist = {'url':'accounting:utils_datalist', 'model':'JRB', 'field':'number'}
    account.as_datalist = {'url':'accounting:utils_datalist', 'model':'COA'}
    account2.as_datalist = {'url':'accounting:utils_datalist', 'model':'COA'}
    cashflow.as_datalist = {'url':'accounting:utils_datalist', 'model':'CCF'}

    class Meta:
        model = JRE
        fields = ('date', 'batch', 'ref', 'number', 'description', 'amount', 'account', 'account2', 'segment', 'cashflow', 'notes')