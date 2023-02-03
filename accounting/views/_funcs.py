from django.http.response import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, reverse, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.db.models import QuerySet, F
from ..models import COA, JRE
from cover.utils import htmx_refresh, htmx_trigger, paginate
from cover import data


# functions for class compositions
def f_test_func(self):
    if isinstance(self, View): user = self.request.user     # if t_test_func is calling by views.generic
    else: user = self.user      # if t_test_func is not called by views.generic
    if user.is_authenticated:
        have_company = user.profile.company
        is_approved = user.profile.comp_stat
        is_valid_employee = have_company and is_approved
        return user.is_authenticated and is_valid_employee
    else: return False


def f_form_valid(self, form):
    obj_instance = form.save(commit=False)
    # set author or editor
    if not hasattr(obj_instance, "author"):
        obj_instance.author = self.request.user 
        obj_instance.edited_by = self.request.user
    else:
        obj_instance.edited_by = self.request.user

    formtype = getattr(form, "form_type")
    if ":" in formtype:
        fmode, ftype = formtype.split(":")
        is_update = ftype == "update"
        if fmode == "double":
            try:
                if is_update:
                    obj_instance.update_pair()
                else:
                    obj_instance.save_pair(self.request.POST.get('account2'))
            except Exception as err:
                err_info = {"title":"Form Error", "head":"Journal syncronization failed!", "msg":f"{err}"}
                return render(self.request, template_name="errors/htmx_modal_err.html", context=err_info)
        else:
            err_info = {"title":"Form Error", "head":"Unknown form type", "msg":f"'{formtype}' is not a valid form type!"}
            return render(self.request, template_name="errors/htmx_modal_err.html", context=err_info)
    else:
        is_update = getattr(form, "form_type") == "update"
        form.save(commit=True)

    use_bs_toast = True     # use bootstrap toast instead of django messages
    if self.request.htmx:
        if use_bs_toast:
            if is_update:
                msg = f"Updated successfully! ({obj_instance})"
            else:
                msg = f"Created successfully! ({obj_instance})"
            self.request.htmx_closemodal = True
            self.request.htmx_message = msg
            response = render(self.request, template_name=self.template_name, context=self.get_context_data())
            # response = htmx_trigger(response, "refresh_table")
            return response
        else:
            response = HttpResponse(status="204")
            htmx_refresh(response)
            if is_update:
                messages.info(self.request, f"Updated successfully! ({obj_instance} - {obj_instance.number})")
            else:
                messages.info(self.request, f"Created successfully! ({obj_instance} - {obj_instance.number})")
            return response


def f_standard_context(self, context, include_sidebar=True):
    # general data
    context.setdefault("model_name", type(self).model.__name__.lower())
    context["page_title"] = type(self).page_title
    context["add_url"] = type(self).model.get_add_url()
    if hasattr(type(self).model, 'get_add_single_url'): context["add_single_url"] = type(self).model.get_add_single_url()

    if include_sidebar:
        # sidebar data
        context["side_menu_group"] = type(self).side_menu_group
        context["side_menu"] = {
            'reports': data.sidebar("report"),
            'master': data.sidebar("master"),
            'transactions': data.sidebar("trans")
        }
    return context


def f_get_list_context_data(self, *args, **kwargs):
    page = self.request.GET.get('page') or 1
    per_page = self.request.GET.get('per_page') or 16

    if hasattr(self, "filter_context_data"): context = self.filter_context_data(**self.kwargs)
    else: context = super(type(self), self).get_context_data(*args, **kwargs)

    # sort queryset data
    if sortby:=self.request.GET.get("sortby"):
        sort_mode = self.request.session.get(f"{type(self).__name__}_sortmode") or "desc"
        if self.request.GET.get("follow_sort"):
            if sort_mode == "asc":
                context[type(self).context_object_name] = context[type(self).context_object_name].order_by(F(sortby).desc())
            else:
                context[type(self).context_object_name] = context[type(self).context_object_name].order_by(F(sortby).asc())
        else:
            context[type(self).context_object_name] = context[type(self).context_object_name].order_by(F(sortby).__getattribute__(sort_mode)())
            # update _sortmode session only if request not perform by paginator
            if sort_mode == "asc": self.request.session[f"{type(self).__name__}_sortmode"] = "desc"
            else: self.request.session[f"{type(self).__name__}_sortmode"] = "asc"

    context = f_standard_context(self, context)     # combined with standard context
    context.setdefault("search_url", type(self).model.get_search_url())
    context[type(self).context_object_name] = paginate(page, context[type(self).context_object_name], paginateBy=per_page)
    context[type(self).table_object_name] = type(self).table(context[type(self).context_object_name], self.table_fields, 
        table_name=type(self).model.__name__.lower(),
        cumulative_balance=context.setdefault("cumulative_balance", False),
        htmx_target=f"div#dataTableContent",
        header_text=self.table_header, 
        filter_data = self.get_table_filters() if hasattr(self, 'get_table_filters') else None,
        ignore_query=("follow_sort",),
        request=self.request)
    return context


def f_get_context_data(self, *args, **kwargs):
    context = super(type(self), self).get_context_data(*args, **kwargs)
    context = f_standard_context(self, context, include_sidebar=False)
    return context


def f_search(request, **kwargs):
    # checks if user have permission to view data
    err_info = {"title":"Forbidden", "head":"Forbidden", "msg":"You dont have permission to access or modify data"}
    allowed_groups = ('accounting_viewer',)
    ingroup = False
    for group in allowed_groups:
        if request.user.groups.filter(name=group).exists(): 
            ingroup = True; break
    if not ingroup:
        if request.htmx: return redirect('cover:error403', msg=err_info['msg'])
        else: return render(request, template_name="errors/htmx_modal_err.html", context=err_info)

    obj_name = "objects" 
    tbl_name = "table_obj"
    # read data from kwargs dictionary
    model = kwargs["model"]
    model_name = "model_name" 
    page_title = kwargs["page_title"]
    table = kwargs["table"]
    table_fields = kwargs["table_fields"]
    table_filters = kwargs.setdefault("table_filters", None)
    header_text = kwargs["header_text"]
    template_name = kwargs["template_name"]
    filter_q = kwargs["filter_q"]

    page = request.GET.get('page') or 1
    per_page = request.GET.get('per_page') or 10


    if isinstance(kwargs.setdefault("querymanager", "objects"), QuerySet):
        context = {obj_name: kwargs['querymanager']}
    else:
        if hasattr(model, kwargs.setdefault('querymanager', 'objects')):
            # dynamically get queryset attribute from model
            # the queryset name come from kwargs['querymanager']
            # because model is a class (not instance), then we need to
            # call __getattribute__ from model super class, in this case the type() class
            context = {obj_name: getattr(model, kwargs.get("querymanager")).all()}
        else:
            context = {obj_name: model.objects.all()}

    context.setdefault(model_name, model.__name__.lower())
    context["page_title"] = page_title
    context['search_url'] = request.get_full_path()
    context['side_menu_group'] = kwargs.get("side_menu_group")
    context['cumulative_balance'] = kwargs.setdefault("cumulative_balance", False)
    context["side_menu"] = {
        'reports': data.sidebar("report"),
        'master': data.sidebar("master"),
        'transactions': data.sidebar("trans")
    }
    context['reporting_period'] = kwargs.get("reporting_period")
    # context[model_name] = model.__name__.lower()
    context[obj_name] = context[obj_name].filter(filter_q)
    context[obj_name] = paginate(page, context[obj_name], paginateBy=per_page)
    context[tbl_name] = table(context[obj_name], table_fields, 
        table_name=model.__name__.lower(),
        # htmx_target=f"div#{model.__name__.lower()}Content",
        cumulative_balance=kwargs.setdefault("cumulative_balance", False),
        htmx_target=f"div#dataTableContent",
        header_text=header_text, 
        filter_data=table_filters,
        ignore_query=("follow_sort",),
        request=request)
    return render(request, template_name=template_name, context=context)