from atexit import register
from datetime import datetime, timezone
from email.policy import default
from pickle import TRUE
from tokenize import group
from django.db import models
from django.utils import timezone

class Post(models.Model):
    server = models.TextField(default='')
    post_id = models.AutoField(primary_key = True)
    secret = models.TextField(default = '')
    post_type = models.TextField(default = '')
    ip = models.TextField(default = '')
    browser = models.TextField(default = '')
    prompt = models.TextField(default = '')
    output = models.TextField(default = '')
    output_type = models.TextField(default = '')
    options = models.TextField(default = '{}')
    count = models.IntegerField(default = 1)
    priority = models.IntegerField(default = 1000)
    mute = models.TextField(default = '')
    select = models.TextField(default = '')
    created = models.DateTimeField(default= timezone.now)
    totask = models.TextField(default = '')
class Task(models.Model):
    server = models.TextField(default = '')
    task_id = models.AutoField(primary_key = True)
    key = models.TextField(default = '')
    post_id = models.IntegerField(default = -1)
    secret = models.TextField(default = '')
    post_type = models.TextField(default = '')
    ip = models.TextField(default = '')
    browser = models.TextField(default = '')
    prompt = models.TextField(default = '')
    output = models.TextField(default = '')
    output_type = models.TextField(default = '')
    options = models.TextField(default = '{}')
    priority = models.IntegerField(default = 1000)
    created = models.DateTimeField(default= timezone.now)
    order = models.IntegerField(default = -1)
#WebServerOnly
class PorticaUser(models.Model):
    pu_id = models.AutoField(primary_key = True)
    user_ids = models.TextField(default = '')
    registered = models.DateTimeField(default = timezone.now)
    name = models.TextField(default = '')
    icon = models.TextField(default = '')
#WebServerOnly
class User(models.Model):
    user_id = models.AutoField(primary_key = True)
    ips = models.TextField(default = '')
    browser  = models.TextField(default = '')#Unique
    group = models.TextField(default = '')
    registered = models.DateTimeField(default = timezone.now)
    mute = models.TextField(default = '')
#WebServerOnly
class TwitterUser(models.Model):
    tu_id = models.AutoField(primary_key = True)
    pu_id = models.IntegerField(default = -1)
    twitter_id = models.TextField(default = '')
    screen_name = models.TextField(default = '')
    icon = models.TextField(default = '')
#WebServerOnly
class GmailUser(models.Model):
    gu_id = models.AutoField(primary_key = True)
    pu_id = models.IntegerField(default = -1)
    mail = models.TextField(default = '')
    icon = models.TextField(default = '')
#Web Server Only
class NetUser(models.Model):
    nu_id = models.AutoField(primary_key = True)
    pu_id = models.IntegerField(default = -1)
    registered = models.TextField(default = timezone.now)
    gpu = models.TextField(default = '')
    gpu_memory = models.FloatField(default = 10.0)
    memory = models.FloatField(default = 32.0)