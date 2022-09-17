from django.utils.safestring import mark_safe
from cover import utils


class TableRowHeader:
    def __init__(self, **kwargs): 
        self.kwargs = kwargs

    def html_tag(self, model, field): 
        return f"<th scope='row' class='{self.kwargs.get('html_class')}'>{str(model.__getattribute__(field))}</th>"

class TableRowCell:
    """
        mask = add masked value.
        val_type = add data type. 
            Example:
                val_type='money', will render as money with comma like 1,350,000
                val_type='date', will render as date like 2022-08-05
    """
    def __init__(self, **kwargs): 
        self.kwargs = kwargs

    def html_tag(self, model, field): 
        if 'mask' in self.kwargs:
            for i in self.kwargs['mask']:
                if i[0]==model.__getattribute__(field):
                    m = i[1]
            return f"<td class='{self.kwargs.get('html_class')}' style='{self.kwargs.get('css_style')}'>{m}</td>"
        else:
            tp = self.kwargs.get('val_type')
            v = str(model.__getattribute__(field))
            if tp == 'date': 
                v = v.split()[0]
            elif tp == "money":
                v = "{:,}".format(int(v))
            return f"<td class='{self.kwargs.get('html_class')}' style='{self.kwargs.get('css_style')}'>{v}</td>"

class TableRowLink:
    def __init__(self, **kwargs): 
        self.kwargs = kwargs

    def html_tag(self, model, field): 
        url_link = model.get_detail_url() if self.kwargs.get('detail_link') else model.get_update_url()
        return f"""<td class='{self.kwargs.get('html_class')}'>
            <a 
                class='{self.kwargs.get('html_class')}'
                type='button'
                data-bs-toggle='modal'
                data-bs-target='#{self.kwargs.get('modal_target')}'
                hx-swap='innerHTML'
                hx-target='#{self.kwargs.get('hx_target')}'
                hx-get='{url_link}'>{str(model.__getattribute__(field))}
            </a></td>"""


class TableHead:
    """
        thead_class = html class for <thead> tag
        html_class = html class for <th> tag
        filter_data = dictionary contain filter data
    """
    def __init__(self, instance, **kwargs):
        self.kwargs = kwargs
        self.target = instance

    def html_tag(self):
        head = f"<thead id='id_{self.target.table_name}' class='{self.kwargs.get('thead_class')}'>"
        if 'header_text' not in self.target.__attributes__:
            self.target.header_text = self.target.fields
        for i, t in zip(self.target.fields, self.target.header_text): 
            head_css_class = self.kwargs.get('html_class').get(i) or self.kwargs.get('html_class').get('_default_css_class')
            if 'filter_data' in self.kwargs and self.kwargs.get('filter_data') and i in self.kwargs.get('filter_data').keys():
                head += f"""<th scope='col' class="{head_css_class}">
                    <a style='color:inherit' class='text-decoration-none' type='button'
                        hx-swap='innerHTML'
                        hx-target='{self.target.htmx_target}'
                        hx-get='{utils.url_query_add(self.kwargs.get("list_url"), **utils._extract_url_query(self.target.request.get_full_path(), self.kwargs.get("ignore_query"), sortby=i))}'
                        >{t.upper()}</a>
                    <a style='color:inherit' class='text-decoration-none'
                    data-bs-toggle='dropdown' data-bs-target='#headerFilterMenu' type='button'>
                    <i class='fa fa-ellipsis-v fa-fw' aria-hidden='true'></i></a>
                    <ul id='headerFilterMenu' class='dropdown-menu dropdown-menu-end'>"""
                for h in self.kwargs.get('filter_data')[i]:
                    if isinstance(h, tuple):
                        head += f"""<li>
                            <a class='dropdown-item'
                                type='button'
                                hx-swap='innerHTML'
                                hx-target='{self.target.htmx_target}'
                                hx-get='{utils.url_query_add(self.kwargs.get("list_url"), **{i.lower():str(h[0])})}'>{h[1]}</a>
                            </li>"""
                    else:
                        head += f"""<li>
                            <a class='dropdown-item'
                                type='button'
                                hx-swap='innerHTML'
                                hx-target='{self.target.htmx_target}'
                                hx-get='{utils.url_query_add(self.kwargs.get("list_url"), **{i.lower():h.lower()})}'>{h}</a>
                            </li>"""
                head += "</ul></th>"
            else:
                head += f"""<th class='{head_css_class}' scope='col'>
                        <a style='color:inherit' class='text-decoration-none' type='button'
                            hx-swap='innerHTML'
                            hx-target='{self.target.htmx_target}'
                            hx-get='{utils.url_query_add(self.kwargs.get("list_url"), **utils._extract_url_query(self.target.request.get_full_path(), self.kwargs.get("ignore_query"), sortby=i))}'
                            >{t.upper()}</a>
                        </th>"""
        head += "</thead>"
        return head

    @property
    def __attributes__(self):
        return list(filter(lambda i: not i.startswith("__"), dir(self)))


class Table:
    """
        header_text:tuple = to set custome header text
        table_header = to set custome table header
    """
    def html_tag(self):
        if 'table_header' in self.__attributes__:
            head = self.__getattribute__('table_header').html_tag()
        else:
            head = TableHead(self).html_tag()
        body = "<tbody>"
        # if cumulative balance
        if self.cumulative_balance:
            body += "<tr>"
            for f in self.fields:
                if hasattr(self, f): 
                    attr = getattr(self, f)
                    if not isinstance(attr, TableRowHeader):
                        body += f"<td class='{attr.kwargs.get('html_class')}'></td>"
                    else:
                        body += f"<th class='{attr.kwargs.get('html_class')}'></th>"
            body += "</tr>"
        for i in self.model:
            body += f"<tr class='{i.get_tablerow_style()}'>"
            for f in self.fields:
                # if f in self.__attributes__:
                if hasattr(self, f):
                    # body += self.__getattribute__(f).html_tag(i, f)
                    body += getattr(self, f).html_tag(i, f)
                else:
                    body += TableRowCell().html_tag(i, f)
            body += "</tr>"
        if len(self.model) < 1:
            body += f"""<tr><td colspan="{len(self.fields)}"><div style='text-align:center'>
                        <strong><i class='fa fa-circle-exclamation me-2 text-danger'></i>no data</strong></div></td></tr>"""
        body += "</tbody>"
        return head + body

    def __init__(self, model, fields:tuple, **kwargs):
        if type(model).__name__ == 'QuerySet' or type(model).__name__ == 'Page':
            self.model = model
        else:
            self.model = model.objects.all()
        self.fields = fields
        # add additional property from kwargs to class instance
        if kwargs:
            for k, v in kwargs.items():
                self.__dict__[k] = v

    def __str__(self):
        return mark_safe(self.html_tag())

    @property
    def __attributes__(self):
        return list(filter(lambda i: not i.startswith("__"), dir(self)))