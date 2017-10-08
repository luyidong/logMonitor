#!/usr/bin/env python
#coding=utf-8
#__author__  = louis,
# __date__   = 2017-08-22 10:22,
#  __email__ = yidongsky@gmail.com,
#   __name__ = forms.py

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import  Profile
from django.contrib.auth  import (
authenticate,
get_user_model,
login,
logout,
)

User = get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=200,label = u"账号")
    password = forms.CharField(widget=forms.PasswordInput,label = u"密码")

    def clean(self,*args,**kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        # print password
        if username and password:
            user = authenticate(username=username,password=password)
            print type(user)
            if not user:
                raise  forms.ValidationError("用户不存在")
            #使用ldap认证，跳过密码验证
            # if not user.check_password(password):
            #     raise forms.ValidationError("密码无效")
            if not user.is_active:
                raise forms.ValidationError("用户不可用")
        return super(UserLoginForm,self).clean(*args,**kwargs)

class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username',
                  'email')

        labels = { 'username':_(u'用户名'),'email':_(u'邮箱地址') }
        # help_texts = {'username':_('some useful help text.'),}
        # error_messages={ 'username':{'max_length':_("this writer name is too long")} }
from django.contrib.auth.models import Group

class ProfileEditForm(forms.ModelForm):

    # b= forms.SelectMultiple(
    #      queryset=Group.objects.filter(user=self.instance.id),
    #
    #      widget=forms.FilteredSelectMultiple("b", is_stacked=False)
    #  )

    group = forms.ModelMultipleChoiceField(
        queryset=None,
        required=True,
        # widget=GroupsSelect,
    )
    class Meta:
        model = Profile
        fields = ('group','wechatNumber','wechatNumber_active','telephoneNumber','telephoneNumber_active')



    def __init__(self, *args, **kwargs):
         self.user = kwargs.pop('user',None)
         super(ProfileEditForm, self).__init__(*args, **kwargs)
         self.fields['group'].queryset=Group.objects.filter(user=self.user)
         self.fields['group'].label = _(u'用户组')
         self.fields['group'].required = False
         #widgets={'group':forms.SelectMultiple(attrs={'readonly': 'True', 'disabled': 'True'})}
         self.fields['group'].widget.attrs["readonly"]= True
         self.fields['group'].widget.attrs["disabled"]= True
