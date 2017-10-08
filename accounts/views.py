#coding=utf-8
from django.shortcuts import render,redirect

from django.contrib.auth  import (
authenticate,
login,
logout,
)
from .models import Profile
from .forms import UserLoginForm,UserEditForm,ProfileEditForm
from django.contrib import messages

def login_view(request):
    next = request.GET.get('next')
    title="登录"
    form = UserLoginForm(request.POST or None)

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get('password')
        user = authenticate(username=username,password=password)
        login(request,user)

        check = Profile.objects.filter(user=user)
        if len(check):
            pass
        else:
            profile_create = Profile.objects.create(user=user)
        if next:
            return  redirect(next)
        return redirect("/")
    return  render(request,"form.html",{"form":form,"title":title})

def logout_view(request):

    title="You're logged out."
    logout(request)

    return  render(request,"form.html",{"title":title})


def profile_edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES,
                                       user=request.user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')

        else:
            messages.warning(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile,user=request.user)
    return render(request, 'edit.html', {'user_form': user_form,'profile_form': profile_form})