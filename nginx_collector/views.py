from django.shortcuts import render

from django.db.models import Sum,Count

from nginx_collector.models import Nginx
from nginx_collector.serializers import NginxSerializer,StatusSerializer

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404,redirect,render_to_response

import json,re

from django.db.models import Q


from rest_framework.generics import ListAPIView
from datetime import date, datetime,timedelta

from django.views.generic import TemplateView,ListView,DeleteView,UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db import connection

from django.core import serializers

from data_collector.models import Alert

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

class NginxViewSet(viewsets.ModelViewSet):
    queryset = Nginx.objects.all()
    serializer_class = NginxSerializer
    permission_classes = (IsAuthenticated,)


    # def post(self, request, format=None):
    #     serializer = NginxSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def


class StatusAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Nginx.objects.all()
    serializer_class = StatusSerializer
    permission_classes = (IsAuthenticated,)

    #https://stackoverflow.com/questions/31920853/aggregate-and-other-annotated-fields-in-django-rest-framework-serializers
    def get_queryset(self):
        return Nginx.objects.annotate(
            sum_status=Count('status')
        )


class nginxstatus(TemplateView):

    template_name = 'nginx/status.html'
    model = Nginx
    paginate_by = 15

    def get_context_data(self, **kwargs):
        ctx = super(TemplateView, self).get_context_data(**kwargs)

        alerts = Alert.objects.filter(is_active=True)

        query = self.request.GET.get("q")
        if query:
            questset_list = Nginx.objects.all()
            nodes_and_status = questset_list.filter(
				Q(node_name__icontains=query)|
				Q(status__icontains=query)
				).values('node_name', 'status').distinct()

        else:
            nodes_and_status = Nginx.objects.all().values('node_name', 'status').distinct()


        paginator = Paginator(nodes_and_status, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            hosts_status = paginator.page(page)
        except PageNotAnInteger:
            hosts_status = paginator.page(1)
        except EmptyPage:
            hosts_status = paginator.page(paginator.num_pages)



        status_data_dict = dict()
        for node_and_status_pair in hosts_status:

            node_name = node_and_status_pair['node_name']
            status = node_and_status_pair['status']
            latest_data_point = Nginx.objects.filter(node_name=node_name, status=status).latest('created')
            # print latest_data_point[]
            latest_data_point.has_alert = self.does_have_alert(latest_data_point, alerts)
            # latest_data_point.has_alerts = self.does_have_alerts(latest_data_point, alerts)

            if latest_data_point.has_alert:
                for  obj in  alerts:
                    alert_regex_data_type  = obj.data_type.encode('utf8')
                    alert_regex_nodename = obj.node_name.encode('utf8')
                    node_name = node_name.strip().encode('utf8')
                    status = status.strip().encode('utf8')
                    match_node= re.findall(alert_regex_nodename,node_name)
                    match_type= re.findall(alert_regex_data_type,status)

                    if match_node and match_type:
                        latest_data_point.threshold = obj.threshold

            data_point_map = status_data_dict.setdefault(node_name,dict())
            data_point_map[status] = latest_data_point

        ctx['status_data_dict'] = status_data_dict
        # print ctx
        ctx[u'is_paginated']    = 'True'
        ctx[u'page_obj'] = hosts_status

        return ctx

    def does_have_alert(self, data_point,alerts):
        # print alerts
        for alert in alerts:
            alert_regex_data_type  = alert.data_type.encode('utf8')
            alert_regex_nodename = alert.node_name.encode('utf8')
            alert_regex_status = float(data_point.status_count.encode('utf8'))
            node_name = data_point.node_name.strip().encode('utf8')
            match_node= re.findall(alert_regex_nodename,node_name)
            match_type= re.findall(alert_regex_data_type,data_point.status)
            if not match_node:
                continue
            if not match_type:
                continue
            if alert.min_value is not None and alert_regex_status < alert.min_value:
                return True
            if alert.max_value is not None and alert_regex_status > alert.max_value:
                return True
        return False

class nginxlistView(ListView):
    template_name = 'nginx/hosts_list.html'
    model =  Nginx
    paginate_by = 20

    def get_queryset(self):

        questset_list = Nginx.objects.order_by('node_name', 'status').values('node_name', 'status',).distinct()

        lists=[]
        for node_and_status_pair  in questset_list:

            node_name = node_and_status_pair['node_name']
            status = node_and_status_pair['status']

            questset_listss=Nginx.objects.filter(node_name__contains=node_name).filter(status=status).values().first()

            for k,v in questset_listss.items():
                if k == 'id':
                    lists.append(format(v))
            questset_data = Nginx.objects.filter(id__in=lists).order_by('node_name', 'status')

        query = self.request.GET.get("q")

        if query:
            questset_list = questset_data.filter(
				Q(node_name__icontains=query)|
				Q(status__icontains=query)
				).distinct()

        else:
            questset_all = Nginx.objects.order_by('node_name', 'status').values('node_name', 'status',).distinct()

            lists=[]
            for node_and_status_pair  in questset_all:

                node_name = node_and_status_pair['node_name']
                status = node_and_status_pair['status']

                questset_filter=Nginx.objects.filter(node_name__contains=node_name).filter(status=status).values().first()

                for k,v in questset_filter.items():
                    if k == 'id':
                        lists.append(format(v))
                questset_list = Nginx.objects.filter(id__in=lists).order_by('node_name', 'status')

        return questset_list

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        list_host = Nginx.objects.values('node_name').distinct()

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

def detail(request,id=None):
    instance = get_object_or_404(Nginx,id=id)
    context = {
        "title":instance.node_name,
        "instance":instance,
    }

    return render(request,"nginx/nginx.html",context)

class Status(View):
    def get(self,request,*args,**kwargs):
        node_name = request.GET.get('node_name')
        status = request.GET.get('status')
        # print(datetime.datetime.now())
        data = Nginx.objects.filter(node_name=node_name).filter(status=status).values('time_local','status','status_count')
        # data = Nginx.objects.extra(select=select).filter(node_name=node_name).values('status','hour').annotate(number=Count('status'))
        #https://mozillazg.github.io/2013/09/django-group-by-hour.html
        # select = {'hour': connection.ops.date_trunc_sql('hour', 'date_created')}
        # data = Nginx.objects.filter(time_local__range=('2017-09-17 14:45:35','2017-09-17 14:55:35')).values('status').annotate(Sum('status_count'))
        # print data
        datas = []
        for qs in data:
            timeline = qs.values()[1]
            # print(qs.values()[1])
            dateStr = timeline.strftime("%Y-%m-%d %H:%M:%S")
            timeUtf = int(datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S").strftime('%s')) * 1000
            dataList = [timeUtf,int(qs.values()[2])]
            # print dataList
            datas.append(dataList)
        # print(datetime.now())
        return HttpResponse(json.dumps(datas),content_type='text/json')

class statusTypeApi(View):

    def get(self,request,*args,**kwargs):
        node_name = request.GET.get('node_name')
        status = Nginx.objects.filter(node_name=node_name).values('status').distinct()
        querylist = []
        for obj in status:
            if obj.values()  not in querylist:
                querylist.append(obj.values())
        return HttpResponse(json.dumps(querylist),content_type='text/json')

class ipApi(View):

    def get(self,request,*args,**kwargs):
        node_name = request.GET.get('node_name')
        status = Nginx.objects.filter(time_local__lt=datetime.now(),
                created__gt=datetime.now()+ timedelta(minutes=-300)).filter(
                node_name=node_name).values('http_x_forwarded_for').annotate(
                Count('http_x_forwarded_for')).order_by('-http_x_forwarded_for__count')[:10]

        data = [ obj for obj in status ]

        return HttpResponse(json.dumps(data),content_type='text/json')

class urlApi(View):

    def get(self,request,*args,**kwargs):
        node_name = request.GET.get('node_name')
        status = Nginx.objects.filter(time_local__lt=datetime.now(),
                created__gt=datetime.now()+ timedelta(minutes=-300)
                ).filter(node_name=node_name).values('status','time_local','body_bytes_sent','request').annotate(
            Count('request')).order_by('-request__count')[:10]
        # print status
        # print status
        data = [ obj for obj in status ]

        return HttpResponse(json.dumps(data,default=json_serial),content_type='text/json')



class statusApi(View):

    '''
    filter(time_local__gt=datetime.datetime.now(),created__lt=datetime.datetime.now()+ datetime.timedelta(minutes=30),
                             )
    '''

    def get(self,request,*args,**kwargs):
        node_name = request.GET.get('node_name')
        # print datetime.now()
        # print datetime.datetime.now()+ datetime.timedelta(minutes=30)
        status = Nginx.objects.filter(time_local__lt=datetime.now(),
                             created__gt=datetime.now()+ timedelta(minutes=-300)).filter(node_name=node_name).values('status').annotate(
            Count('status')).order_by('-status__count')[:10]
        # print status
        data = [ obj for obj in status ]

        querylist = []
        for obj in status:
            if obj.values()  not in querylist:
                querylist.append(obj.values())
        # print querylist

        return HttpResponse(json.dumps(querylist),content_type='text/json')


def  aboutView(request):
    template_name = 'nginx/about.html'
    return render(request,template_name)