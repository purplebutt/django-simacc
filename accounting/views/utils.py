import string
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.db.models.base import ModelBase
from ..models import *
from company.models import Company

def get_datalist(request, model):
    model_name = model

    # replace punctuation and space from model arguments
    # to prevent some bad guys hacking with python code
    # because we need to use eval() to create object from string
    for pun in string.punctuation: model_name = model_name.replace(pun, "")
    model_name = model_name.replace(" ", "")

    try:
        mdl = eval(model_name)
    except:
        return HttpResponseBadRequest(f"There's no model for {model}")

    if isinstance(mdl, ModelBase):
        if hasattr(mdl, 'get_with_number'):
            dl = mdl.get_with_number('|')
            context = {'datalist':dl} 
        else:
            if field:=request.GET.get('field'):
                dl = mdl.actives.values_list(field)
                if request.GET.get('upper'):
                    dl = set(map(lambda i: str(i[0]).upper(), dl))
                else:
                    dl = set(map(lambda i: i[0], dl))
                context = {'datalist':dl}
            else:
                if hasattr(mdl.objects.first(), 'number'):
                    context = {'datalist':mdl.actives.order_by('number').all()}
                else:
                    context = {'datalist':mdl.actives.all()}
        return render(request, template_name="apps/accounting/_utils/datalist.html", context=context)
    else:
        return HttpResponseBadRequest(f"There's no model for {model}")
        