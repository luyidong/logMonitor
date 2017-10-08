#!/usr/bin/env python
#coding=utf-8
#__author__  = louis,
# __date__   = 2017-08-08 23:41,
#  __email__ = yidongsky@gmail.com,
#   __name__ = mail.py

from django.core.mail import send_mail as django_send_mail
from django.core.mail import EmailMultiAlternatives
from datetime import datetime as dt
from time import sleep
import threading

def send_mail(subject, message, from_email, recipient_list,fail_silently=False, auth_user=None, auth_password=None):
    class Sender(threading.Thread):
        def run(self):
            django_send_mail(subject, message, from_email,recipient_list, fail_silently, auth_user, auth_password)
    s=Sender()
    s.start()
    return True

def send_multi_mail(subject, text_content, html_content, from_email, recipient_list, fail_silently=False):
    class Sender(threading.Thread):
        def run(self):
            msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
    s=Sender()
    s.start()



