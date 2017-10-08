"""logMonitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url,include
from django.contrib import admin

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from accounts.views import (login_view,logout_view,profile_edit)

from data_collector.views import (
    StatusView,
    AlertListView,
    NewAlertView,
    EditAlertView,
    DeleteAlertView,
    HostListView,
    HostDetailView,
    RecordDataApiView,
    SelectDataApiView,
    DataTypeApiView,
)


from rest_framework.routers import DefaultRouter
from nginx_collector import  views
from nginx_collector.views import (
    NginxViewSet,
    StatusAPIView,
    Status,
    detail,
    statusTypeApi,
    ipApi,
    # ipListView,
    urlApi,
    statusApi,
    nginxlistView,
    nginxstatus,
    aboutView,
)

from rest_framework import routers
# router = routers.SimpleRouter()

router = DefaultRouter()
router.register(r'nginx',views.NginxViewSet)
router.register(r'status',views.StatusAPIView)


urlpatterns = [
    # url(r'^', include('data_collector.urls',namespace="collector")),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),

    # url(r'^$', login_required(StatusView.as_view()), name='status'),
    url(r'^alerts/$', login_required(AlertListView.as_view()), name='alerts-list'),
    url(r'^alerts/new/$', login_required(NewAlertView.as_view()), name='alerts-new'),
    url(r'^alerts/(?P<pk>\d+)/edit/$', login_required(EditAlertView.as_view()),name='alerts-edit'),
    url(r'^alerts/(?P<pk>\d+)/delete/$', login_required(DeleteAlertView.as_view()),name='alerts-delete'),
    url(r'^record/$', csrf_exempt(RecordDataApiView.as_view()),name='record-data'),
    url(r'^select/$', SelectDataApiView.as_view(),name='Select-data'),
    url(r'^datatype/$', DataTypeApiView.as_view(),name='datatype'),
    url(r'^hosts/$', login_required(HostListView.as_view()), name='hosts-list'),
    url(r'^(?P<id>\d+)/$', HostDetailView, name='hosts-detail'),
    url(r'^profile_edit/$', profile_edit, name='profile_edit'),
    url(r'^api/',include(router.urls,namespace='api')),
    url(r'^api-auth/',include('rest_framework.urls',namespace='rest_framework')),
    url(r'^nginx/',Status.as_view(),name='nginx-ajax'),
    url(r'^statustype/',statusTypeApi.as_view(),name='status-type'),
    url(r'^ipapi/',ipApi.as_view(),name='ip-api'),
    # url(r'^iplist/',ipListView.as_view(),name='ip-list'),
    url(r'^urlapi/',urlApi.as_view(),name='url-list'),
    url(r'^statusapi/',statusApi.as_view(),name='status-api'),
    url(r'^nginxlist/$', login_required(nginxlistView.as_view()), name='nginx-list'),
    url(r'^$', login_required(nginxstatus.as_view()), name='nginx-status'),

    url(r'^detail/(?P<id>\d+)/$', detail, name='nginx-detail'),
    url(r'^about/$',aboutView,name='about'),

]
