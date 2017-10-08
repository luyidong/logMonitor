#!/usr/bin/env python
#coding=utf-8
#__author__  = louis,
# __date__   = 2017-08-16 14:49,
#  __email__ = yidongsky@gmail.com,
#   __name__ = urls.py

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


from .views import (
    StatusView,
    AlertListView,
    NewAlertView,
    EditAlertView,
    DeleteAlertView,
    HostListView,
    HostDetailView,
    RecordDataApiView,
    SelectDataApiView
)

urlpatterns = [

    url(r'^alerts/$', login_required(AlertListView.as_view()), name='alerts-list'),
    url(r'^alerts/new/$', login_required(NewAlertView.as_view()), name='alerts-new'),
    url(r'^alerts/(?P<pk>\d+)/edit/$', login_required(EditAlertView.as_view()),name='alerts-edit'),
    url(r'^alerts/(?P<pk>\d+)/delete/$', login_required(DeleteAlertView.as_view()),name='alerts-delete'),
    url(r'^record/$', csrf_exempt(RecordDataApiView.as_view()),name='record-data'),
    url(r'^select/$', SelectDataApiView.as_view(),name='Select-data'),
    url(r'^hosts/$', login_required(HostListView.as_view()), name='hosts-list'),
    url(r'^(?P<id>\d+)/$', HostDetailView, name='hosts-detail'),
    url(r'^$', StatusView.as_view(), name="status"),
]
