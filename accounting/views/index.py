from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def homepage(request):
    ctx = {}
    return render(request, template_name="apps/accounting/homepage.html", context=ctx)