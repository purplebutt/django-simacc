from accounting.html import base
from ..models import COH, COA, CCF, BSG, JRB, JRE


class COHTable(base.Table):
    model = COH
    number = base.TableRowHeader(html_class="border")
    name = base.TableRowLink(
        hx_target=f'{model.__name__.lower()}UpdateModalContent',
        modal_target=f'{model.__name__.lower()}UpdateModal',
        html_class='text-decoration-none',
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
        self.table_header = base.TableHead(self, html_class="text-warning text-center border", thead_class="bg-secondary",
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class COATable(base.Table):
    model = COA
    number = base.TableRowHeader(html_class="border")
    normal = base.TableRowCell(mask=COA._normal_balance, html_class="border")
    is_active = base.TableRowCell(html_class="border", mask=[(True, "Yes"), (False, "No")])
    is_cashflow = base.TableRowCell(html_class="border", mask=[(True, "Yes"), (False, "No")])
    name = base.TableRowLink(
        hx_target=f'{model.__name__.lower()}UpdateModalContent',
        modal_target=f'{model.__name__.lower()}UpdateModal',
        html_class='text-decoration-none'
    )

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        self.table_header = base.TableHead(self, html_class="text-warning text-center border", thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class CCFTable(base.Table):
    model = CCF
    number = base.TableRowHeader(html_class="border")
    flow = base.TableRowCell(mask=CCF._flow, html_class="border")
    activity = base.TableRowCell(mask=CCF._activities, html_class="border")
    is_active = base.TableRowCell(html_class="border")
    name = base.TableRowLink(
        hx_target=f'{model.__name__.lower()}UpdateModalContent',
        modal_target=f'{model.__name__.lower()}UpdateModal',
        html_class='text-decoration-none'
    )

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        self.table_header = base.TableHead(self, html_class="text-warning text-center border", thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class BSGTable(base.Table):
    model = BSG
    number = base.TableRowHeader(html_class="border")
    group = base.TableRowHeader(html_class="border")
    is_active = base.TableRowCell(html_class="border")
    name = base.TableRowLink(
        hx_target=f'{model.__name__.lower()}UpdateModalContent',
        modal_target=f'{model.__name__.lower()}UpdateModal',
        html_class='text-decoration-none'
    )

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        self.table_header = base.TableHead(self, html_class="text-warning text-center border", thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class JRBTable(base.Table):
    model = JRB
    created = base.TableRowCell(html_class="border", val_type="date")
    description = base.TableRowCell(html_class="border")
    group = base.TableRowCell(html_class="border")
    is_active = base.TableRowCell(html_class="border")
    balance = base.TableRowCell(html_class="border text-end", val_type="money", marker=('not:0', 'text-danger'))
    entries = base.TableRowCell(html_class="border text-end", val_type="money")
    number = base.TableRowLink(
        hx_target=f'{model.__name__.lower()}UpdateModalContent',
        modal_target=f'{model.__name__.lower()}UpdateModal',
        html_class='text-decoration-none'
    )

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        self.table_header = base.TableHead(self, html_class="text-warning text-center border", thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())


class JRETable(base.Table):
    model = JRE
    date = base.TableRowCell(html_class="border", css_style="font-size:small")
    number = base.TableRowLink(
        hx_target=f'{model.__name__.lower()}UpdateModalContent',
        modal_target=f'{model.__name__.lower()}UpdateModal',
        html_class='text-decoration-none'
    )
    batch = base.TableRowCell(html_class="border", css_style="font-size:small")
    ref = base.TableRowCell(html_class="border")
    description = base.TableRowCell(html_class="border", css_style="font-size:small")
    group = base.TableRowCell(html_class="border", mask=JRE._type)
    amount = base.TableRowCell(html_class="border text-end", val_type="money")
    account = base.TableRowCell(html_class="border", css_style="font-size:small")
    segment = base.TableRowCell(html_class="border")
    cashflow = base.TableRowCell(html_class="border", css_style="font-size:small")
    notes = base.TableRowCell(html_class="border")
    is_active = base.TableRowCell(html_class="border", mask=[(True,"Yes"),(False,"No")])
    author = base.TableRowCell(html_class="border")

    def __init__(self, model, fields, **kwargs):
        super(type(self), self).__init__(model, fields, **kwargs)
        # custom table header (can only be add on __init__ method because it's need self/instance)
        self.table_header = base.TableHead(self, html_class="text-warning text-center border", thead_class="bg-secondary", 
            filter_data=kwargs.get('filter_data'), ignore_query=kwargs.get('ignore_query'), list_url=type(self).model.get_list_url())
