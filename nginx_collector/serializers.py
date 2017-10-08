#!/usr/bin/env python
#coding=utf-8
__author__ = "yidong.lu"
__email__ = "yidongsky@gmail.com"

import re
from rest_framework import serializers
from nginx_collector.models import Nginx
from data_collector.models import Alert
from  data_collector.utils.notification_tool import Notification


class NginxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nginx
        fields = '__all__'
        # fields = ('id', )
    def validate(self,data):
        # data['remote_addr']
        # data['remote_user']
        # data['time_local']
        # data['request']
        # data['status']
        # data['body_bytes_sent']
        # data['http_referer']
        # data['http_user_agent']
        # data['request_time']
        # data['http_x_forwarded_for']
        node_name=data['node_name']
        data_type=data['status']
        data_value=data['status_count']
        time_local=data['time_local']
        alerts = Alert.objects.filter(is_active=True)
        send_alert=self.does_have_alert(node_name,data_type,data_value,time_local,alerts)

        return  data


    def does_have_alert(self, node_name,data_type,data_value,time_local,alerts):
        # print alerts
        for alert in alerts:
            alert_regex_data_type  = alert.data_type.encode('utf8')
            alert_regex_nodename = alert.node_name.encode('utf8')
            alert_regex_status = float(data_value.encode('utf8'))
            node_name = node_name.strip().encode('utf8')
            match_node= re.findall(alert_regex_nodename,node_name)
            match_type= re.findall(alert_regex_data_type,data_type)
            if not match_node:
                continue
            if not match_type:
                continue
            if alert.min_value is not None and alert_regex_status < alert.min_value:
                return True
            if alert.max_value is not None and alert_regex_status > alert.max_value:

                send_data = Notification(alert,node_name,data_type,time_local,data_value)

                try:
                    send_data.send_wecharts()
                except:
                    print "Error: unable to start send_wecharts"

                try:
                    send_data.send_mail()
                except:
                    print "Error: unable to send_mail"

                try:
                    send_data.send_sms()
                except:
                    print "Error: unable to start send_sms"

                return True

        return False




class StatusSerializer(serializers.ModelSerializer):
    sum_status = serializers.FloatField()

    class Meta:
        model = Nginx
        # fields = '__all__'
        fields = ('id','node_name','status','sum_status' )