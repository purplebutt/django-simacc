from django.urls.base import reverse_lazy
from accounting.html import base
from ..models import COH, COA, CCF, BSG, JRB, JRE


class COHTable(base.Table):
    model = COH
    number = base.TableRowLink(
        hx_target='UpdateModalContent',
        modal_target='UpdateModal',
        html_class='text-decoration-none fw-bold'
    )
    name = base.TableRowLink(
        hx_target='DetailModalContent',
        modal_target='DetailModal',
        html_class='text-decoration-none fw-bold text-secondary',
        detail_link=True
    )
    report = base.TableRowCell(
        mask=COH._reports,
        html_class='border'
    )
    group = base.TableRowCell(
        mask=COH._account_group,
        html_class='border'
    )

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        head_css_class = {'_default_css_class': 'text-warning text-center border'}
        self.table_header = base.TableHead(self, html_class=head_css_class, thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class COATable(base.Table):
    model = COA
    number = base.TableRowLink(
        hx_target='UpdateModalContent',
        modal_target='UpdateModal',
        html_class='text-decoration-none fw-bold text-primary'
    )
    name = base.TableRowLink(
        hx_target='DetailModalContent',
        modal_target='DetailModal',
        html_class='text-decoration-none fw-bold text-secondary',
        detail_link=True
    )
    normal = base.TableRowCell(mask=COA._normal_balance, html_class="border")
    is_active = base.TableRowCell(html_class="border", mask=[(True, "Yes"), (False, "No")])
    is_cashflow = base.TableRowCell(html_class="border", mask=[(True, "Yes"), (False, "No")])
    debit = base.TableRowCell(html_class="border text-end", val_type="money")
    credit = base.TableRowCell(html_class="border text-end", val_type="money")
    balance = base.TableRowCell(html_class="border text-end", val_type="money")

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        head_css_class = {'_default_css_class': 'text-warning text-center border'}
        self.table_header = base.TableHead(self, html_class=head_css_class, thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class CCFTable(base.Table):
    model = CCF
    number = base.TableRowLink(
        hx_target='UpdateModalContent',
        modal_target='UpdateModal',
        html_class='text-decoration-none fw-bold'
    )
    name = base.TableRowLink(
        hx_target='DetailModalContent',
        modal_target='DetailModal',
        html_class='text-decoration-none fw-bold text-secondary',
        detail_link=True
    )
    flow = base.TableRowCell(mask=CCF._flow, html_class="border")
    activity = base.TableRowCell(mask=CCF._activities, html_class="border")
    is_active = base.TableRowCell(html_class="border")

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        head_css_class = {'_default_css_class': 'text-warning text-center border'}
        self.table_header = base.TableHead(self, html_class=head_css_class, thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class BSGTable(base.Table):
    model = BSG
    number = base.TableRowLink(
        hx_target='UpdateModalContent',
        modal_target='UpdateModal',
        html_class='text-decoration-none fw-bold'
    )
    name = base.TableRowLink(
        hx_target='DetailModalContent',
        modal_target='DetailModal',
        html_class='text-decoration-none fw-bold text-secondary',
        detail_link=True
    )
    group = base.TableRowHeader(html_class="border")
    is_active = base.TableRowCell(html_class="border")

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        head_css_class = {'_default_css_class': 'text-warning text-center border'}
        self.table_header = base.TableHead(self, html_class=head_css_class, thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class JRBTable(base.Table):
    model = JRB
    number = base.TableRowLink(
        hx_target='UpdateModalContent',
        modal_target='UpdateModal',
        html_class='text-decoration-none fw-bold'
    )
    description = base.TableRowLink(
        hx_target='DetailModalContent',
        modal_target='DetailModal',
        html_class='text-decoration-none fw-bold text-secondary',
        detail_link=True
    )
    created = base.TableRowCell(html_class="border", val_type="date")
    group = base.TableRowCell(html_class="border")
    is_active = base.TableRowCell(html_class="border")
    balance = base.TableRowCell(html_class="border text-end", val_type="money")
    entries = base.TableRowCell(html_class="border text-end", val_type="money")

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        head_css_class = {'_default_css_class': 'text-warning text-center border'}
        self.table_header = base.TableHead(self, html_class=head_css_class, thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class JRETable(base.Table):
    model = JRE
    date = base.TableRowCell(html_class="border", css_style="font-size:small")
    number = base.TableRowLink(
        hx_target='UpdateModalContent',
        modal_target='UpdateModal',
        html_class='text-decoration-none fw-bold'
    )
    batch = base.TableRowLink(
        hx_target='DetailModalContent',
        modal_target='DetailModal',
        html_class='text-decoration-none fw-bold text-secondary d-none d-lg-table-cell',
        detail_link=True
    )
    # batch = base.TableRowCell(html_class="border d-none d-lg-table-cell", css_style="font-size:small")
    ref = base.TableRowCell(html_class="border d-none d-lg-table-cell")
    description = base.TableRowCell(html_class="border d-none d-lg-table-cell", css_style="font-size:small")
    group = base.TableRowCell(html_class="border", mask=JRE._type)
    amount = base.TableRowCell(html_class="border text-end", val_type="money")
    account = base.TableRowCell(html_class="border", css_style="font-size:small")
    segment = base.TableRowCell(html_class="border d-none d-lg-table-cell")
    cashflow = base.TableRowCell(html_class="border d-none d-lg-table-cell", css_style="font-size:small")
    notes = base.TableRowCell(html_class="border d-none d-lg-table-cell")
    is_active = base.TableRowCell(html_class="border d-none d-lg-table-cell", mask=[(True,"Yes"),(False,"No")])

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        head_css_class = {'_default_css_class': 'text-warning text-center border',
                          'batch': 'text-warning text-center border d-none d-lg-table-cell',
                          'ref': 'text-warning text-center border d-none d-lg-table-cell',
                          'description': 'text-warning text-center border d-none d-lg-table-cell',
                          'segment': 'text-warning text-center border d-none d-lg-table-cell',
                          'cashflow': 'text-warning text-center border d-none d-lg-table-cell',
                          'notes': 'text-warning text-center border d-none d-lg-table-cell',
                          'is_active': 'text-warning text-center border d-none d-lg-table-cell',
                          }
        self.table_header = base.TableHead(self, html_class=head_css_class, thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class TBTable(base.Table):
    model_name = 'tb'
    list_url = reverse_lazy("accounting:report_tb")
    number = base.TableRowHeader(html_class="border")
    normal = base.TableRowCell(mask=COA._normal_balance, html_class="border")
    is_active = base.TableRowCell(html_class="border", mask=[(True, "Yes"), (False, "No")])
    is_cashflow = base.TableRowCell(html_class="border", mask=[(True, "Yes"), (False, "No")])
    name = base.TableRowLink(
        hx_target='UpdateModalContent',
        modal_target='UpdateModal',
        html_class='text-decoration-none'
    )
    previous = base.TableRowCell(html_class="border text-end", val_type="money")
    debit = base.TableRowCell(html_class="border text-end", val_type="money")
    credit = base.TableRowCell(html_class="border text-end", val_type="money")
    balance = base.TableRowCell(html_class="border text-end", val_type="money")

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        head_css_class = {'_default_css_class': 'text-warning text-center border'}
        self.table_header = base.TableHead(self, html_class=head_css_class, thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).list_url)