from django.http.response import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, reverse, redirect
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, ListView
from django.db.models import F
from ..models import COA, JRE
from cover.utils import htmx_refresh, htmx_trigger, has_attribute, paginate
from cover import data


# functions for class compositions
def f_user_ingroup(self):
    ingroup = self.request.user.groups.filter(name=type(self).allowed_group).exists()
    return ingroup


def f_test_func(self):
    return self.request.user.is_authenticated


def f_get(self, *args, **kwargs):
    # checks if user have permission to update or modify data
    err_info = {"title":"Forbidden", "head":"Forbidden", "msg":"You dont have permission to access or modify data"}
    if isinstance(self, CreateView):
        if not f_user_ingroup(self):
            if not self.request.htmx:
                return HttpResponseForbidden(err_info["msg"])
            else:
                return render(self.request, template_name="errors/htmx_modal_err.html", context=err_info)
    elif isinstance(self, ListView):
        if self.request.htmx:
            self.template_name = type(self).htmx_template   # change to htmx template
    return super(type(self), self).get(self.request, *args, **kwargs)


def f_post(self, *args, **kwargs):
    # checks if user have permission to update or modify data
    err_info = {"title":"Forbidden", "head":"Forbidden", "msg":"You dont have permission to access or modify data"}
    if not f_user_ingroup(self):
        if not self.request.htmx:
            return HttpResponseForbidden(err_info["msg"])
        else:
            return render(self.request, template_name="errors/htmx_modal_err.html", context=err_info)
    else:
        return super(type(self), self).post(self.request, *args, **kwargs)


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
            obj_instance.save_pair(self.request.POST.get('account2'))
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
            response = render(self.request, template_name=type(self).template_name, context=self.get_context_data())
            response = htmx_trigger(response, "refresh_table")
            return response
        else:
            response = HttpResponse(status="204")
            htmx_refresh(response)
            if is_update:
                messages.info(self.request, f"Updated successfully! ({obj_instance} - {obj_instance.number})")
            else:
                messages.info(self.request, f"Created successfully! ({obj_instance} - {obj_instance.number})")
            return response


def f_get_context_data(self, *args, **kwargs):
    if isinstance(self, ListView):
        page = self.request.GET.get('page') or 1
        per_page = self.request.GET.get('per_page') or 10

        if has_attribute(self, "filter_context_data"):
            context = self.filter_context_data(**self.kwargs)
        else:
            context = super(type(self), self).get_context_data(*args, **kwargs)

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
                if sort_mode == "asc":
                    self.request.session[f"{type(self).__name__}_sortmode"] = "desc"
                else:
                    self.request.session[f"{type(self).__name__}_sortmode"] = "asc"

        context = f_standard_context(self, context)
        context["search_url"] = type(self).model.get_search_url()
        context[type(self).context_object_name] = paginate(page, context[type(self).context_object_name], paginateBy=per_page)
        context[type(self).table_object_name] = type(self).table(context[type(self).context_object_name], type(self).table_fields, 
            table_name=type(self).model.__name__.lower(),
            htmx_target=f"div#{type(self).model.__name__.lower()}Content",
            header_text=type(self).table_header, 
            filter_data=type(self).table_filters,
            ignore_query=("follow_sort",),
            request=self.request)
        return context
    else:
        context = super(type(self), self).get_context_data(*args, **kwargs)
        context["is_user_allowed"] = f_user_ingroup(self)
        # general data
        context["model_name"] = type(self).model.__name__.lower()
        context["page_title"] = type(self).page_title
        context["add_url"] = type(self).model.get_add_url()
        if hasattr(type(self).model, 'get_add_single_url'): context["add_single_url"] = type(self).model.get_add_single_url()
        return context


def f_standard_context(self, context):
    # general data
    context["model_name"] = type(self).model.__name__.lower()
    context["page_title"] = type(self).page_title
    context["add_url"] = type(self).model.get_add_url()
    if hasattr(type(self).model, 'get_add_single_url'): context["add_single_url"] = type(self).model.get_add_single_url()

    # sidebar data
    context["report"] = data.sidebar("report")
    context["master"] = data.sidebar("master")
    context["trans"] = data.sidebar("trans")

    return context


def f_search(request, **kwargs):
    obj_name = "objects" 
    tbl_name = "table_obj"
    # read data from kwargs dictionary
    model = kwargs["model"]
    model_name = "model_name" 
    table = kwargs["table"]
    table_fields = kwargs["table_fields"]
    table_filters = kwargs["table_filters"]
    header_text = kwargs["header_text"]
    template_name = kwargs["template_name"]
    filter_q = kwargs["filter_q"]

    page = request.GET.get('page') or 1
    per_page = request.GET.get('per_page') or 10

    context = {obj_name: model.objects.all()}
    context[model_name] = model.__name__.lower()
    context[obj_name] = context[obj_name].filter(filter_q)
    context[obj_name] = paginate(page, context[obj_name], paginateBy=per_page)
    context[tbl_name] = table(context[obj_name], table_fields, 
        table_name=model.__name__.lower(),
        htmx_target=f"div#{model.__name__.lower()}Content",
        header_text=header_text, 
        filter_data=table_filters,
        ignore_query=("follow_sort",),
        request=request)
    return render(request, template_name=template_name, context=context)