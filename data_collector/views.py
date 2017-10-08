#!/usr/bin/env python
#coding=utf-8
#__author__  = louis,
# __date__   = 2017-08-08 10:22,
#  __email__ = yidongsky@gmail.com,
#   __name__ = view.py


from django.views.generic import TemplateView,ListView,DeleteView,UpdateView
from data_collector.models import DataPoint,Alert

from accounts.models import Profile
from utils.sms import send_multi_sms

from utils.wechart import send_multi_wechart

from django.core.urlresolvers import reverse
from django.views.generic import CreateView

#record API
from django.forms.models import modelform_factory
from django.http.response import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.http.response import HttpResponseForbidden
from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import datetime,json
from django.conf import settings

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy

from mail import send_multi_mail

from django.db.models import Q

from django.shortcuts import render,get_object_or_404,redirect,render_to_response

from  data_collector.utils.notification_tool import Notification

class StatusView(TemplateView):

    template_name = 'status.html'
    model = DataPoint
    paginate_by = 20

    def get_context_data(self, **kwargs):

        ctx = super(TemplateView, self).get_context_data(**kwargs)

        alerts = Alert.objects.filter(is_active=True)

        query = self.request.GET.get("q")
        if query:
            questset_list = DataPoint.objects.all()
            nodes_and_data_types = questset_list.filter(
				Q(node_name__icontains=query)|
				Q(data_type__icontains=query)
				).values('node_name', 'data_type').distinct()

        else:
            nodes_and_data_types = DataPoint.objects.all().values('node_name', 'data_type').distinct()


        paginator = Paginator(nodes_and_data_types, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            hosts_status = paginator.page(page)
        except PageNotAnInteger:
            hosts_status = paginator.page(1)
        except EmptyPage:
            hosts_status = paginator.page(paginator.num_pages)



        status_data_dict = dict()
        for node_and_data_type_pair in hosts_status:

            node_name = node_and_data_type_pair['node_name']
            data_type = node_and_data_type_pair['data_type']
            latest_data_point = DataPoint.objects.filter(node_name=node_name, data_type=data_type).latest('datetime')

            latest_data_point.has_alert = self.does_have_alert(latest_data_point, alerts)

            querylist=Alert.objects.filter(node_name=node_name, data_type=data_type).values()

            for item in querylist:

                # print i['threshold']

                latest_data_point.threshold = item['threshold']
            # print latest_data_point.threshold
            data_point_map = status_data_dict.setdefault(node_name,dict())

            data_point_map[data_type] = latest_data_point


        ctx['status_data_dict'] = status_data_dict
        ctx[u'is_paginated']    = 'True'
        ctx[u'page_obj'] = hosts_status

        return ctx

    def does_have_alert(self, data_point, alerts):
        for alert in alerts:
            if alert.node_name and data_point.node_name != alert.node_name:
                continue
            if alert.data_type != data_point.data_type:
                continue
            if alert.min_value is not None and data_point.data_value < alert.min_value:
                return True
            if alert.max_value is not None and data_point.data_value > alert.max_value:
                return True

        return False


class AlertListView(ListView):
    template_name = 'alerts_list.html'
    model = Alert
    paginate_by = 10

    def get_queryset(self,):
        questset_list = Alert.objects.all()
        query = self.request.GET.get("q")
        if query:
            questset_list = questset_list.filter(
				Q(node_name__icontains=query)|
				Q(data_type__icontains=query)
				).distinct()
        return questset_list

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        list_host = Alert.objects.values('node_name').distinct()
        paginator = Paginator(list_host, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            list_hosts = paginator.page(page)
        except PageNotAnInteger:
            list_hosts = paginator.page(1)
        except EmptyPage:
            list_hosts = paginator.page(paginator.num_pages)

        context['list_hosts'] = list_hosts

        return context


class NewAlertView(CreateView):
    template_name = 'create_or_update_alert.html'
    model = Alert
    success_url = reverse_lazy('Alerts')
    success_message = 'Alert successfully created!!!!'
    fields = ['data_type', 'min_value', 'max_value', 'node_name', 'users','groups','threshold','interval_unit','interval_value','is_active']

    def create(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(NewAlertView, self).create(request, *args, **kwargs)


    def get_success_url(self):
        return reverse('alerts-list')

class EditAlertView(UpdateView):
    template_name = 'create_or_update_alert.html'
    model = Alert
    success_url = reverse_lazy('Alerts')
    success_message = 'List successfully saved!!!!'

    fields = ['data_type', 'min_value', 'max_value', 'node_name', 'users','groups','threshold','interval_unit','interval_value','is_active']

    def update(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EditAlertView, self).update(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('alerts-list')


class DeleteAlertView(DeleteView):
    template_name = 'delete_alert.html'
    model = Alert
    success_url = reverse_lazy('Alert')
    success_message = "Thing was deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteAlertView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('alerts-list')

class HostListView(ListView):
    template_name = 'hosts_list.html'
    model =   DataPoint
    paginate_by = 20

    def get_queryset(self):

        questset_list = DataPoint.objects.order_by('node_name', 'data_type').values('node_name', 'data_type',).distinct()

        lists=[]
        for node_and_data_type_pair  in questset_list:

            node_name = node_and_data_type_pair['node_name']
            data_type = node_and_data_type_pair['data_type']

            questset_listss=DataPoint.objects.filter(node_name__contains=node_name).filter(data_type=data_type).values().first()

            for k,v in questset_listss.items():
                if k == 'id':
                    lists.append(format(v))
            questset_data = DataPoint.objects.filter(id__in=lists).order_by('node_name', 'data_type')

        query = self.request.GET.get("q")

        if query:
            questset_list = questset_data.filter(
				Q(node_name__icontains=query)|
				Q(data_type__icontains=query)
				).distinct()

        else:
            questset_all = DataPoint.objects.order_by('node_name', 'data_type').values('node_name', 'data_type',).distinct()

            lists=[]
            for node_and_data_type_pair  in questset_all:

                node_name = node_and_data_type_pair['node_name']
                data_type = node_and_data_type_pair['data_type']

                questset_filter=DataPoint.objects.filter(node_name__contains=node_name).filter(data_type=data_type).values().first()

                for k,v in questset_filter.items():
                    if k == 'id':
                        lists.append(format(v))
                questset_list = DataPoint.objects.filter(id__in=lists).order_by('node_name', 'data_type')

        return questset_list

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        list_host = DataPoint.objects.values('node_name').distinct()

        paginator = Paginator(list_host, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            list_hosts = paginator.page(page)
        except PageNotAnInteger:
            list_hosts = paginator.page(1)
        except EmptyPage:
            list_hosts = paginator.page(paginator.num_pages)

        context['list_hosts'] = list_hosts
        return context


def HostDetailView(request, id=None):
    instance = get_object_or_404(DataPoint, id=id)
    context = {
        "title":instance.node_name,
        "instance":instance,
    }


    return render(request,"host_detail.html",context)

class RecordDataApiView(View):
    def post(self, request, *args, **kwargs):
        # Check if the secret key matches
        if request.META.get('HTTP_AUTH_SECRET') != 'supersecretkey':
            return HttpResponseForbidden('Auth key incorrect')
        form_class = modelform_factory(DataPoint, fields=['node_name','data_type','data_value'])
        form = form_class(request.POST)
        print form

        if form.is_valid():
            node_name=form.cleaned_data['node_name']
            data_type=form.cleaned_data['data_type']
            data_value=form.cleaned_data['data_value']
            # datetime=form.cleaned_data['datetime']

            alerts = Alert.objects.filter(is_active=True)

            send_alert=self.does_have_alert(node_name,data_type,data_value, alerts)

            if send_alert:
                 pass
            else:
                print 'DataPoint status ok'

            form.save()

            return HttpResponse()
        else:
            return HttpResponseBadRequest('Bad Request')


    def does_have_alert(self, node_name,data_type,data_value, alerts):
        for alert in alerts:
            if alert.node_name and node_name != alert.node_name:
                continue
            if alert.data_type != data_type:
                continue
            if alert.min_value is not None and data_value < alert.min_value:
                return True
            if alert.max_value is not None and data_value > alert.max_value:
                alerts = str(data_value)

                send_data = Notification(alert,alert.node_name,alert.data_type,alerts)
                send_data.send_mail()
                send_data.send_sms()
                send_data.send_wechart()

                return True

        return False

class SelectDataApiView(View):

    def get(self,request,*args,**kwargs):
        node_name = request.GET.get('node_name')
        date_type = request.GET.get('date_type')
        data = DataPoint.objects.filter(node_name=node_name).filter(data_type=date_type).values('datetime','data_type','data_value')
        datas = []
        for qs in data:
            timeline = qs.values()[2]
            # print type(timeline)
            dateStr = timeline.strftime("%Y-%m-%d %H:%M:%S")
            timeUtf = int(datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S").strftime('%s')) * 1000
            dataList = [timeUtf,qs.values()[0]]
            datas.append(dataList)
        return HttpResponse(json.dumps(datas),content_type='text/json')

class DataTypeApiView(View):

    def get(self,request,*args,**kwargs):
        node_name = request.GET.get('node_name')
        data_type = DataPoint.objects.filter(node_name=node_name).values('data_type').distinct()
        querylist = []
        for q in data_type:
            if q.values()  not in querylist:
                querylist.append(q.values())
        return HttpResponse(json.dumps(querylist),content_type='text/json')