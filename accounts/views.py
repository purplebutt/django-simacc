from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls.base import reverse_lazy
from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm, ProfileImageForm
from cover.utils import htmx_refresh
from cover import data



class ProfileDetailView(generic.DeleteView):
    model = Profile
    context_object_name = 'object'
    template_name = 'accounts/profile.html'


@login_required
def my_profile(request):
    ctx = {}
    uform = UserUpdateForm(instance=request.user)
    pform = ProfileUpdateForm(instance=request.user.profile)
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if uform.is_valid() and pform.is_valid():
            uform.save(); pform.save()
            msg = messages.info(request, f"Your profile has been updated successfully!")        
            return redirect("accounts:myprofile")
    ctx['uform'] = uform
    ctx['pform'] = pform
    ctx['forms'] = [uform, pform]
    return render(request, template_name="account/myprofile.html", context=ctx)

@login_required
def image_update(request):
    ctx = {}
    ctx['object'] = request.user.profile
    form = ProfileImageForm()
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, instance=request.user.profile, files=request.FILES)
        if form.is_valid():
            form.save()
            msg = f"Image for {request.user.username.capitalize()} has been updated successfully!"
            if not request.htmx:
                messages.info(request, msg)        
                response = HttpResponse("Image updated successfully", status=204)
                return htmx_refresh(response)
            else:
                request.htmx_closemodal = True
                request.htmx_message = msg
                return render(request, template_name="account/image.html", context=ctx)
    ctx['form'] = form
    return render(request, template_name="account/image.html", context=ctx)

