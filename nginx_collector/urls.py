#!/usr/bin/env python
#coding=utf-8
__author__ = "yidong.lu"
__email__ = "yidongsky@gmail.com"

from django.conf.urls import url,include
from django.contrib import admin


from rest_framework.routers import DefaultRouter
from nginx_collector.views import (
    NginxViewSet,
    StatusAPIView,

)

nginx_list = NginxViewSet.as_view({
    'get': 'list'
    'post': 'create'
    'delete': 'destory'
})

status_list = StatusAPIView.as_view({
    'get':'list'
})

urlpatterns = [
    # url(r'^status',StatusAPIView.as_view(),name='nginx-status'),
    # url(r'^', include('data_collector.urls',namespace="collector")),

]

urlpatterns = format_suffix_patterns(patterns('nginx_collector.views',
    url(r'^nginx/$', nginx_list, name='nginx_list'),
    url(r'^status/$', status_list, name='status_list'),
)
