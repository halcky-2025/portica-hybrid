"""
Definition of views.
"""

from asyncore import read
from collections import OrderedDict
from doctest import OutputChecker
from http import server
from itertools import count
from posixpath import split
import secrets
import subprocess
import datetime
from html.entities import name2codepoint
from pickle import NONE
from sys import stderr
from wsgiref.util import request_uri
from django.shortcuts import render
from django.shortcuts import redirect
from django.template import Context, loader
from django.http import HttpRequest
from django.http import HttpResponse
from django.views import View
from django.core.files.storage import FileSystemStorage
import base64
import json
import os
import shutil
import random
from app import models
import deepl
from app import app
from django.db.models import Q
MigradeID = 1
import tweepy
import threading
import time
import sys
sys.path.append("..")
from PorticaServer import settings

programs = {}

#Post
#Task
#Home
#twitter WebOnly
#gmail WebOnly
#setting
#info
#list
#select
#mute
#db
class InputView(View):
    def get(self, request, *args, **kwargs):
        assert isinstance(request, HttpRequest)
        name = request.GET.get('name', 'a')
        print(name)
        #try:
        t = loader.get_template(name + '/input.html')
        html_str = t.render({})
        #except Exception as e:
        #    html_str = str(e)
        return HttpResponse(html_str)
passwordChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
def GeneratePassword(length):
    stri = ''
    for i in range(length):
        stri += random.choice(passwordChars);
    return stri
web = False
m = None
#m = 'maintenance'
myip = ''
ps = []
post_type = None
server = 'http://localhost:5000'
def schedule_post():
    global post_type
    if len(ps) == 0 and len(orders) > 0 and settings.Server == False:
        Getup(orders[0])
def schedule_task():
    if len(ps) == 0 and len(torders) > 0 and settings.Server == False:
        order = lowtorder()
        if order:
            Getup(order['order'])
last_order = datetime.datetime.now()

def addtoders(post_id, order):
    ors = torders.get(post_id, None)
    if order.get('count'):
        torders[post_id] = {'count': order['count'], 'totask': app.projects[order['post_type']].get('totask', ''), 'exe': '', 'before': app.projects[order['post_type']].get('before', None), 'output':[], 'input': [None] * order['count']}
        ors = torders[post_id]
    else:
        orde = order['order']
        if 0 <= orde and orde < len(ors['input']):
            ors['input'][orde] = order
def lowtorder():
    l = 6553600
    targetors = None
    key = None
    n = -1
    for k in torders:
        if torders[k]['exe'] and torders[k].get('before', None):
            continue
        ors = torders[k]['input']
        
        if len(ors) == 0:
            continue
        if torders[k]['totask'] == 'pararell':
            n2 = -1
            for i in range(len(ors)):
                if ors[i]:
                    n2 = i
                    break
            if n2 == -1:
                continue
        else:
            n2 = len(torders[k]['output'])
            if ors[n2] == None:
                continue
        l2 = len(ors) - len(torders[k]['output'])
        if l2 < l:
            l = l2
            key = k
            targetors = ors
            n = n2
    if targetors:
        return {'post_id': key, 'n': n, 'order': targetors[n]}
    else:
        return None
def outputtorder(post_id):
    output = torders[post_id]['output']
    before = torders[post_id].get('before', None)
    r = []
    if before:
        for i in range(before):
            if len(output) - 1 - i >= 0:
                task = output[len(output) - 1 - i]
                r.append({'output_type': task.output_type, 'output': task.output})
            else:
                break
    return r
def deltorder(post_id, n):
    targetors = torders[post_id]['input']
    if targetors:
        order = targetors[n]
        targetors[n] = None
        torders[post_id]['exe'] = order['secret']
        return order
    else:
        return None
def finishtorder(task):
    ors = torders.get(task.post_id, None)
    if ors:
        ors['output'].append(task)
        ors['exe'] = ''
def Getup(order):
    global last_order
    global post_type
    frdir = app.projects[order['post_type']].get('task', None)
    if frdir:
        if len(ps) > 0:
            for p in ps:
                p.terminate()
        f = frdir
        if app.Windows:
            command = [frdir + 'python/python', 'task.py', '--server', server]
            p = subprocess.Popen(command, stderr=subprocess.STDOUT, cwd=f)
        else:
            cmd = '. ' + 'venv/bin/activate && python3 ' + 'task.py'
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, executable='/bin/dash', cwd=f)
            t = threading.Thread(target=send, args=(p,))
            t.start()
        ps.append(p)
        post_type = frdir
        last_order = datetime.datetime.now()
def send(p):
    while True:
        # バッファから1行読み込む.
        line = p.stdout.readline()
        if line:
            print(line)
            i = 1
        time.sleep(1)
def schedule_order():
    global last_order
    global ps
    delta = datetime.datetime.now() - last_order
    '''if delta.seconds > 60 * 2:
        for p in ps:
            p.terminate()
        ps = []'''
    if len(orders) > 0 or len(torders) > 0:
        last_order = datetime.datetime.now()
def getip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合: 転送経路の先頭要素を取得する。
        ip = ip.split(',')[0]
    else:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがない場合: 直接接続なので'REMOTE_ADDR'ヘッダを参照する。
        ip = request.META.get('REMOTE_ADDR')
    return ip
def SetValuePost(post, values, files):
    options = json.loads(post.options)
    for k in files.keys():
        print(k)
        fsb = FileSystemStorage(location='app/static/' + post.post_type)
        extension = os.path.splitext(files.getlist(k)[0].name)[1].lower()
        stri = ''
        loop = True
        another = False
        while(loop):
            if extension == '.jpg':
                stri = GeneratePassword(12) + '.jpg'
            elif extension == '.jpeg':
                stri = GeneratePassword(11) + '.jpeg'
            elif extension == '.png':
                stri = GeneratePassword(12) + '.png'
            elif extension == '.hevc':
                stri = GeneratePassword(11) + '.hevc'
            else:
                stri = GeneratePassword(12) + extension
            loop = fsb.exists(stri)
        fsb.save(stri, files.getlist(k)[0])
        filename = stri
        with open('app/static/' + post.post_type + '/' + filename, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
            options[k] = {'address': post.post_type + '/' + filename, 'content': content}
    for k in values.keys():
        print(k)
        if k == 'prompt':
            post.prompt = values[k]
            en = post.prompt
            
            for ch in post.prompt:
                if ch.isascii():
                    continue
                else:
                    translator = deepl.Translator("4853b89d-4a70-086f-fd46-fae9b691009f")    
                    en = str(translator.translate_text(post.prompt, target_lang="EN-US"))
                    break
            options['en_prompt'] = en
        elif k == 'count':
            post.count = int(values[k])
        elif k == 'post_type':
            noope = True
        elif k == 'mute':
            post.mute = values[k]
        else:
            options[k] = values[k]
    post.options = json.dumps(options)
def SetValueTask(post, values, files):
    options = json.loads(post.options)
    secret = None
    for k in files.keys():
        print(k)
        fsb = FileSystemStorage(location='app/static/' + post.post_type)
        extension = os.path.splitext(files.getlist(k)[0].name)[1].lower()
        stri = ''
        loop = True
        another = False
        while(loop):
            if extension == '.jpg':
                stri = GeneratePassword(12) + '.jpg'
            elif extension == '.jpeg':
                stri = GeneratePassword(11) + '.jpeg'
            elif extension == '.png':
                stri = GeneratePassword(12) + '.png'
            elif extension == '.hevc':
                stri = GeneratePassword(11) + '.hevc'
            else:
                stri = GeneratePassword(12) + extension
            loop = fsb.exists(stri)
        fsb.save(stri, files.getlist(k)[0])
        filename = stri
        with open('app/static/' + post.post_type + '/' + filename, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
            options[k] = {'address': post.post_type + '/' + filename, 'content': content}
    for k in values.keys():
        if k == 'prompt':
            post.prompt = values[k]
            en = post.prompt
            
            for ch in post.prompt:
                if ch.isascii():
                    continue
                else:
                    translator = deepl.Translator("4853b89d-4a70-086f-fd46-fae9b691009f")    
                    en = str(translator.translate_text(post.prompt, target_lang="EN-US"))
                    break
            options['en_prompt'] = en
        if k == 'secret':
            secret = values[k]
        if k == 'order':
            post.order = int(values[k])
        if k == 'post_id':
            post.post_id = int(values[k])
        elif k == 'post_type':
            noope = True
        elif k == "key":
            post.key = values[k]
        else:
            options[k] = values[k]
    post.options = json.dumps(options)
    return secret
class PostView(View):
    def get(self, request, *args, **kwargs):
        assert isinstance(request, HttpRequest)
        ip = getip(request)
        browser = request.session.get('browser', None)
        group = request.session.get('group', None)
        if group is None:
            group = random.randint(0, 1)
            request.session['group'] = group
        if browser is None:
            browser = GeneratePassword(16)
            request.session['browser'] = browser
            user = models.User(browser=browser, ips = ip, group = group, mute= request.session.get('mute', ''))
            user.save()
        if m is not None:
            if ip != myip:
                return HttpResponse(":m")


        if len(orders) > 0 and orders[0]['date']:
            if (orders[0]['date'] - datetime.datetime.now()).seconds > 5 * 60:
                print('AniOni')
                schedule_post()
        return render(request, 'app/post.html',  {'projects': app.projects})
    def post(self, request, *args, **kwargs):
        assert isinstance(request, HttpRequest)
        ip = getip(request)
        browser = request.session.get('browser', None)
        group = request.session.get('group', None)
        if group is None:
            group = random.randint(0, 1)
            request.session['group'] = group
        if browser is None:
            browser = GeneratePassword(16)
            request.session['browser'] = browser
            user = models.User(browser=browser, ips = ip, group = group, mute= request.session.get('mute', ''))
            user.save()
        userlist = models.User.objects.filter(browser = browser)[:1]
        if len(userlist) == 0:
            user = models.User(browser=browser, ips = ip, group = group, mute= request.session.get('mute', ''))
            user.save()
        else:
            user = userlist[0]
            ok = False
            for uip in user.ips.split(';'):
                if ip == uip:
                    ok = True
                    break
            if ok == False:
                user.ips += ";" + ip
                user.save()
        if m is not None:
            if ip != myip:
                return HttpResponse(":m")
        count = request.session.get('count', 0)
        date = request.session.get('date', None)
        if date is None:
            date = datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=+9))).day
            request.session['date'] = date
        now = datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=+9)))
        if date != now.day:
            count = 0
        count += 1
        request.session['count'] = count

        post_type = request.POST.get('post_type', None)
        if post_type is None:
            return HttpResponse('')
        post = models.Post(post_type = post_type, ip = ip, browser = browser, options = '{}', priority = 100, totask = app.projects[post_type].get('totask', ''))
        SetValuePost(post, request.POST, request.FILES)
        if post.prompt != '':
            secret = GeneratePassword(16)
            post.secret = secret
            o = app.projects[post.post_type].get("order", None)
            if o:
                post.output_type = 'ordering'
            post.save()
            post = models.Post.objects.filter(secret = secret)[0]
            if post.totask == '':
                order = {'type': 'post', 'count': post.count, 'secret': secret, 'post_type': post.post_type, 'prompt': post.prompt, 'options': json.loads(post.options)}
                order['date'] = None
                orders.append(order)
            else:
                post.output_type = 'tasks'
                addtoders(post.post_id, {'post_type': post.post_type, 'count': 1000})
            if o:
                order2 = {'post_id': post.post_id, 'type': 'post', 'count': post.count, 'secret': secret, 'post_type': post.post_type, 'prompt': post.prompt, 'options': json.loads(post.options)}
                if app.Windows:
                    command = [o + 'python/python', o + 'order.py']
                    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, text=True, encoding="utf8")
                else:
                    cmd = '. ' + o + 'venv/bin/activate && python3 ' + o + 'order.py'
                    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, text=True, encoding="utf8", shell=True, executable='/bin/dash')
                v = proc.communicate(json.dumps(order2) + '\n')[0]
                print(v)
                values = json.loads(v)
                SetValuePost(post, values, {})
                post.save()
            else:
                post.save()
            if post.totask != '':
                torders[post.post_id]['input'] = torders[post.post_id]['input'][0: post.count]
                torders[post.post_id]['count'] = post.count
            schedule_post()
            return HttpResponse(json.dumps({'id': post.post_id, 'secret': secret}))
        else:
            return HttpResponse('')
class TaskView(View):
    def post(self, request, *args, **kwargs):
        assert isinstance(request, HttpRequest)
        ip = getip(request)
        browser = request.session.get('browser', None)
        group = request.session.get('group', None)
        if group is None:
            group = random.randint(0, 1)
            request.session['group'] = group
        if browser is None:
            browser = GeneratePassword(16)
            request.session['browser'] = browser
            user = models.User(browser=browser, ips = ip, group = group, mute= request.session.get('mute', ''))
            user.save()
        userlist = models.User.objects.filter(browser = browser)[:1]
        if len(userlist) == 0:
            user = models.User(browser=browser, ips = ip, group = group, mute= request.session.get('mute', ''))
            user.save()
        else:
            user = userlist[0]
            ok = False
            for uip in user.ips.split(';'):
                if ip == uip:
                    ok = True
                    break
            if ok == False:
                user.ips += ";" + ip
                user.save()
        if m is not None:
            if ip != myip:
                return HttpResponse(":m")
        count = request.session.get('count', 0)
        date = request.session.get('date', None)
        if date is None:
            date = datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=+9))).day
            request.session['date'] = date
        now = datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=+9)))
        if date != now.day:
            count = 0
        count += 1
        request.session['count'] = count

        
        post = models.Task(ip = ip, browser = browser, options = '{}', priority = 100)
        secret = SetValueTask(post, request.POST, request.FILES)
        post.post_type = request.POST.get('post_type', None)
        if post.post_type is None:
            return HttpResponse('')
        SetValueTask(post, request.POST, request.FILES)
        if post.prompt != '' and secret:
            p = models.Post.objects.filter(post_id = post.post_id)
            if len(p) == 1:
                p = p[0]
                if p.secret == secret:
                    secret = GeneratePassword(16)
                    order = {'type': 'task', 'secret': secret, 'post_type': post.post_type, 'prompt': post.prompt, 'options': json.loads(post.options), 'key': post.key, 'order': post.order}
                    order['date'] = None
                    addtoders(post.post_id, order)
                    post.secret = secret
                    post.save()
                    schedule_task()
                    return HttpResponse(json.dumps(order))
        return HttpResponse('')
class ListView(View):
    def get(self, request, *args, **kwargs):
        global order_list
        assert isinstance(request, HttpRequest)
        ip = getip(request)
        browser = request.session.get('browser', None)
        group = request.session.get('group', None)
        if group is None:
            group = random.randint(0, 1)
            request.session['group'] = group
        if browser is None:
            browser = GeneratePassword(16)
            request.session['browser'] = browser
            user = models.User(browser=browser, ips = ip, group = group, mute= request.session.get('mute', ''))
            user.save()
        c = int(request.GET.get('c', '1'))
        pi = None
        if c == 2:
            post_list = models.Post.objects.filter(browser = browser).order_by('-post_id')[ : 9]
            l = len(post_list)
            pk = post_list
        elif c == 1:
            pk = []
            for p in posts:
                if p.mute =='' or p.mute == 'new':
                    pk.append(p)
                elif p.mute == 'mute1':
                    if p.browser == browser:
                        pk.append(p)  
                elif p.mute == 'mute2':
                    if p.browser == browser or p.ip == ip:
                        pk.append(p)
                if len(pk) == 10:
                    break
        elif c == 3:
            pk = models.Post.objects.filter(select = 'select').order_by('?')[:10]
            pl = models.Post.objects.filter(select = 'select', browser = browser).order_by('?')[:1]
            if len(pl) != 0:
                pi = pl[0]
        elif c == 4:
            secret = request.GET.get('secret', '')
            post = models.Post.objects.filter(secret = secret)[ : 1][0]
            return render(request, post.post_type + '/description.html', {'id': post.post_id, 'secret': post.secret, 'post_type': post.post_type, "prompt": post.prompt, 'options': json.loads(post.options), 'output': post.output, 'output_type': post.output_type})
        datas = []
        num = 0
        for p in pk:
            t = loader.get_template(p.post_type + '/item.html')
            cx = {'id': p.post_id, 'secret': p.secret, 'post_type': p.post_type, "prompt": p.prompt, 'output': p.output, 'output_type': p.output_type, 'options': json.loads(p.options), 'num': num, 'c': c}
            txt = t.render(cx)
            datas.append(txt)
            num += 1
        if pi is not None:
            t = loader.get_template(p.post_type + '/item.html')
            cx = {'id': pi.post_id, 'secret': pi.secret, 'post_type': pi.post_type, "prompt": pi.prompt, 'output': pi.output, 'output_type': pi.output_type, 'options': pi.options, 'num': num, 'c': c}
            datas.insert(random.randint(1, 8), t.render(cx))
        return HttpResponse(json.dumps(datas))
ordersexec = []
tordersexec = []
def delorders(post):
    if isinstance(post, models.Task):
        oexec = tordersexec
    else:
        oexec = ordersexec
    for i in range(len(oexec)):
        if post.secret == oexec[i]['order']['secret']:
            del oexec[i]
            break
def checkorders():
    now = datetime.datetime.now()
    print(now)
    i = 0
    while i < len(ordersexec):
        order = ordersexec[i]['order']
        delta = now - order['date']
        if delta.seconds > 30:
            del ordersexec[i]
            orders.append(order)
            continue
        i += 1
    i = 0
    while i < len(tordersexec):
        order = tordersexec[i]['order']
        delta = now - order['date']
        print(delta)
        if delta.seconds > 30:
            print(order)
            post_id = tordersexec[i]['post_id']
            del tordersexec[i]
            torders[post_id]['exe'] = ''
            addtoders(post_id, order)
            continue
        i += 1
class OutputView(View):
    def post(self, request, *args, **kwargs):
        global orders
        assert isinstance(request, HttpRequest)
        secret = request.POST.get('secret', '')
        tag = request.POST.get('tag', None)
        typo = request.POST.get('type', None)
        print(tag)
        if typo == 'task':
            post = models.Task.objects.filter(secret = secret)[:1]
        else:
            post = models.Post.objects.filter(secret = secret)[:1]
        if len(post) == 1:
            post = post[0]
            post.output_type = tag
            if tag == 'err':
                output = request.POST.get('output', '')
                post.output = output
            elif tag == 'img':
                output = request.FILES.getlist('output')[0]
                fsb = FileSystemStorage(location='app/static/' + post.post_type)
                extension = os.path.splitext(output.name)[1].lower()
                stri = ''
                loop = True
                another = False
                while(loop):
                    if extension == '.jpg':
                        stri = GeneratePassword(12) + '.jpg'
                    elif extension == '.jpeg':
                        stri = GeneratePassword(11) + '.jpeg'
                    elif extension == '.png':
                        stri = GeneratePassword(12) + '.png'
                    elif extension == '.hevc':
                        stri = GeneratePassword(11) + '.hevc'
                    else:
                        stri = GeneratePassword(12) + extension
                    loop = fsb.exists(stri)
                fsb.save(stri, output)
                filename = stri
                post.output = post.post_type + '/' + filename
            elif tag == 'json':
                output = request.POST.get('output', '')
                post.output = output
            if typo != 'task':
                posts.insert(0, post)
                if len(posts) > 100:
                    del posts[len(posts) - 1]
                if banip.get(post.ip, False) == True or banbrowser.get(post.browser, False) == True:
                        if post.mute == '':
                            post.mute = 'mute2'
                if post.mute == 'mute1':
                    post.prompt = "こっそり★" + post.prompt
            post.save()
            if post.server:
                import urllib3
                http = urllib3.PoolManager()
                if tag == 'img':
                    with open('app/static/' + post.output, "rb") as f:
                        output = f.read()
                    output= ('update' + extension, output, 'image/png')
                dic = {'secret': secret, 'output_type': tag, 'output': output}
                r = http.request('POST', post.server + '/output', fields=dic)
                order = r.data.decode('utf-8')
                typo = 'server'
            if typo == 'task':
                p = models.Post.objects.filter(post_id = post.post_id)[0]
                if p.output != '':
                    p.output += ';'
                else:
                    p.output_type = 'tasks'
                p.output += post.secret
                p.save()
                finishtorder(post)
                l = len(p.output.split(';'))
                if l == p.count:
                    del torders[post.post_id]
                    p.output_type = 'tasksOK'
                    tasks = models.Task.objects.filter(post_id = p.post_id)
                    options = json.loads(p.options)
                    options['tasks'] = {}
                    for task in tasks:
                        if task.output_type == 'img':
                            op= task.output
                        elif task.output_type == 'err' or task.output_type == 'json':
                            op = task.output
                        options['tasks'][task.key] = {"type": task.output_type, "output": op}
                    order = {'type': 'post', 'count': p.count, 'secret': p.secret, 'post_type': p.post_type, 'prompt': p.prompt, 'options': options}
            
                    o = app.projects[p.post_type].get("complete", None)
                    if o:
                        if app.Windows:
                            command = [o + 'python/python', o + 'complete.py']
                            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf8")
                        else:
                            cmd = '. ' + o + 'venv/bin/activate && python3 ' + o + 'complete.py'
                            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, text=True, encoding="utf8", shell=True, executable='/bin/dash')
                        v = proc.communicate(json.dumps(order) + '\n')[0]
                        r = json.loads(v)
                        tag = r.get('output_type', None)
                        output = r.get('output', None)
                        p.output_type = tag
                        if tag == 'json':
                            p.output = output
                        elif tag == 'mov':
                            name = r.get('name', None)
                            fsb = FileSystemStorage(location='app/static/' + p.post_type)
                            extension = os.path.splitext(name)[1].lower()
                            stri = ''
                            loop = True
                            another = False
                            while(loop):
                                if extension == '.mp4':
                                    stri = GeneratePassword(12) + '.mp4'
                                elif extension == '.mov':
                                    stri = GeneratePassword(12) + '.mov'
                                elif extension == '.avi':
                                    stri = GeneratePassword(12) + '.avi'
                                else:
                                    stri = GeneratePassword(12) + extension
                                loop = fsb.exists(stri)
                            filename = p.post_type + '/' + stri
                            with open('app/static/' + filename, 'wb') as f:
                                init_img_content = base64.b64decode(output)
                                f.write(init_img_content)
                            p.output = filename
                        posts.insert(0, p)
                        if len(posts) > 100:
                            del posts[len(posts) - 1]
                        if banip.get(p.ip, False) == True or banbrowser.get(p.browser, False) == True:
                             if p.mute == '':
                                 p.mute = 'mute2'
                        if p.mute == 'mute1':
                            p.prompt = "こっそり★" + p.prompt
                    p.save()
                    schedule_post()
            delorders(post)
        schedule_order()

        return HttpResponse('OK')
class OrderView(View):
    def post(self, request, *args, **kwargs):
        global orders
        assert isinstance(request, HttpRequest)
        secret = request.POST.get('secret', '')
        tag = request.POST.get('tag', None)
        typo = request.POST.get('type', None)
        print(tag)
        if typo == 'task':
            post = models.Task.objects.filter(secret = secret)[:1]
        else:
            post = models.Post.objects.filter(secret = secret)[:1]
        if len(post) == 1:
            post = post[0]
            post.output_type = tag
            if tag == 'err':
                output = request.POST.get('output', '')
                post.output = output
            elif tag == 'img':
                output = request.FILES.getlist('output')[0]
                fsb = FileSystemStorage(location='app/static/' + post.post_type)
                extension = os.path.splitext(output.name)[1].lower()
                stri = ''
                loop = True
                another = False
                while(loop):
                    if extension == '.jpg':
                        stri = GeneratePassword(12) + '.jpg'
                    elif extension == '.jpeg':
                        stri = GeneratePassword(11) + '.jpeg'
                    elif extension == '.png':
                        stri = GeneratePassword(12) + '.png'
                    elif extension == '.hevc':
                        stri = GeneratePassword(11) + '.hevc'
                    else:
                        stri = GeneratePassword(12) + extension
                    loop = fsb.exists(stri)
                fsb.save(stri, output)
                filename = stri
                post.output = post.post_type + '/' + filename
            elif tag == 'json':
                output = request.POST.get('output', '')
                post.output = output
            if typo != 'task':
                posts.insert(0, post)
                if len(posts) > 100:
                    del posts[len(posts) - 1]
                if post.ip != '' and post.browser != '' and (banip.get(post.ip, False) == True or banbrowser.get(post.browser, False) == True):
                        if post.mute == '':
                            post.mute = 'mute2'
                if post.mute == 'mute1':
                    post.prompt = "こっそり★" + post.prompt
            post.save()
            if post.server:
                import urllib3
                http = urllib3.PoolManager()
                if tag == 'img':
                    with open('app/static/' + post.output, "rb") as f:
                        output = f.read()
                    output= ('update' + extension, output, 'image/png')
                dic = {'secret': secret, 'tag': tag, 'output': output, 'type': typo}
                r = http.request('POST', post.server + '/output', fields=dic)
                order = r.data.decode('utf-8')
                typo = 'server'
            if typo == 'task':
                p = models.Post.objects.filter(post_id = post.post_id)[0]
                if p.output != '':
                    p.output += ';'
                else:
                    p.output_type = 'tasks'
                p.output += post.secret
                p.save()
                finishtorder(post)
                l = len(p.output.split(';'))
                if l == p.count:
                    del torders[post.post_id]
                    p.output_type = 'tasksOK'
                    tasks = models.Task.objects.filter(post_id = p.post_id)
                    options = json.loads(p.options)
                    options['tasks'] = {}
                    for task in tasks:
                        if task.output_type == 'img':
                            op= task.output
                        elif task.output_type == 'err' or task.output_type == 'json':
                            op = task.output
                        options['tasks'][task.key] = {"type": task.output_type, "output": op}
                    order = {'type': 'post', 'count': p.count, 'secret': p.secret, 'post_type': p.post_type, 'prompt': p.prompt, 'options': options}
            
                    o = app.projects[p.post_type].get("complete", None)
                    if o:
                        if app.Windows:
                            command = [o + 'python/python', o + 'complete.py']
                            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf8")
                        else:
                            cmd = '. ' + o + 'venv/bin/activate && python3 ' + o + 'complete.py'
                            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, text=True, encoding="utf8", shell=True, executable='/bin/dash')
                        v = proc.communicate(json.dumps(order) + '\n')[0]
                        r = json.loads(v)
                        tag = r.get('output_type', None)
                        output = r.get('output', None)
                        p.output_type = tag
                        if tag == 'json':
                            p.output = output
                        elif tag == 'mov':
                            name = r.get('name', None)
                            fsb = FileSystemStorage(location='app/static/' + p.post_type)
                            extension = os.path.splitext(name)[1].lower()
                            stri = ''
                            loop = True
                            another = False
                            while(loop):
                                if extension == '.mp4':
                                    stri = GeneratePassword(12) + '.mp4'
                                elif extension == '.mov':
                                    stri = GeneratePassword(12) + '.mov'
                                elif extension == '.avi':
                                    stri = GeneratePassword(12) + '.avi'
                                else:
                                    stri = GeneratePassword(12) + extension
                                loop = fsb.exists(stri)
                            filename = p.post_type + '/' + stri
                            with open('app/static/' + filename, 'wb') as f:
                                init_img_content = base64.b64decode(output)
                                f.write(init_img_content)
                            p.output = filename
                        posts.insert(0, p)
                        if len(posts) > 100:
                            del posts[len(posts) - 1]
                        if banip.get(p.ip, False) == True or banbrowser.get(p.browser, False) == True:
                             if p.mute == '':
                                 p.mute = 'mute2'
                        if p.mute == 'mute1':
                            p.prompt = "こっそり★" + p.prompt
                    p.save()
                    schedule_post()
            delorders(post)
        schedule_order()

        return send()
def send():
    if len(orders) > 0:
        order = orders[0]
        if settings.Server == False and  post_type != app.projects[order['post_type']].get('task', None):
            Getup(order)
            return HttpResponse('')
        order['date'] = datetime.datetime.now()
        ordersexec.append({'order': order})
        del orders[0]
        return HttpResponse(json.dumps(order, default=json_serial))
    elif len(torders) > 0:
        r = lowtorder()
        print(r)
        if r:
            order = r['order']
            post_id = r['post_id']
            n = r['n']
            if settings.Server == False and post_type != app.projects[order['post_type']].get('task', None):
                Getup(order)
                return HttpResponse('')
            order['date'] = datetime.datetime.now()
            tordersexec.append({'post_id': post_id, 'order': order})
            order= deltorder(post_id, n)
        
            o = app.projects[order['post_type']].get("prepare", None)
            if o:
                if app.Windows:
                    command = [o + 'python/python', o + 'prepare.py']
                    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf8")
                else:
                    cmd = '. ' + o + 'venv/bin/activate && python3 ' + o + 'prepare.py'
                    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, text=True, encoding="utf8", shell=True, executable='/bin/dash')
                output = outputtorder(post_id)
                v = proc.communicate(json.dumps(order, default=json_serial) + '\n' + json.dumps(output) + '\n')[0]
                ou = json.loads(v)
                task = models.Task.objects.filter(secret = order['secret'])[0]
                SetValueTask(task, ou, {})
                order = {'type': 'task', 'secret': task.secret, 'post_type': task.post_type, 'prompt': task.prompt, 'options': json.loads(task.options), 'key': task.key, 'order': task.order}

            return HttpResponse(json.dumps(order, default=json_serial))
    return receive()
rorders = []
def receive():
    if len(rorders) > 0:
        order = rorders[0]
        del rorders[0]
        return HttpResponse(json.dumps(order))
    elif settings.Server == False and servers:
        import urllib3
        http = urllib3.PoolManager()
        dic = {}
        for server in servers:
            try:
                r = http.request('POST', server + '/order', fields=dic)
                order = json.loads(r.data.decode('utf-8'))
                pt = order.get('post_type', None)
                if pt is None:
                    continue
                type = order.get('type', None)
                secret = order.get('secret', '')
                prompt = order.get('prompt', '')
                options = order.get('options', {})
                if type == 'post':
                    post = models.Post(post_type = pt, secret = secret, prompt = prompt, options = json.dumps(options), server = server)
                else:
                    key = order.get('key', '')
                    orde = order.get('order', -1)
                    post = models.Task(post_type = pt, secret = secret, prompt = prompt, options = json.dumps(options), key = key, order = orde, server = server)
                post.save()
                if post_type != app.projects[pt].get('task', None):
                    rorders.append(order)
                    Getup(order)
                    return HttpResponse('')
                return HttpResponse(json.dumps(order))
            except:
                n = 1
    return HttpResponse(json.dumps({}))
class ServerView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'server')
    def post(self, request, *args, **kwargs):
        server = request.POST.get('server', '')
        import urllib3
        servers.append(server)
        return render(request, 'server')
servers = ['https://portica.cloud']
def json_serial(obj):
    # 日付型の場合には、文字列に変換します
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    # 上記以外はサポート対象外.
    raise TypeError ("Type %s not serializable" % type(obj))

class PostInfo(View):
    def get(self, request, *args, **kwargs):
        ip = getip(request)
        if ip != myip:
            return HttpResponse("")
        posts = models.Post.objects.all()
        datas = []
        for p in posts:
            datas.append({'id': p.post_id, 'secret': p.secret, 'post_type': p.post_type, 'ip': p.ip, 'browser': p.browser, 'prompt': p.prompt, 'output': p.output, 'output_type': p.output_type, 'options': p.options, 'count': p.count, 'priority': p.priority, 'mute': p.mute, 'select': p.select, 'created': str(p.created)})
        response = HttpResponse(json.dumps(datas), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=info.json'
        return response

class TaskInfo(View):
    def get(self, request, *args, **kwargs):
        ip = getip(request)
        if ip != myip:
            return HttpResponse("")
        posts = models.Task.objects.all()
        datas = []
        for p in posts:
            datas.append({'id': p.task_id, 'key': p.key, 'post_id': p.post_id, 'secret': p.secret, 'post_type': p.post_type, 'ip': p.ip, 'browser': p.browser, 'prompt': p.prompt, 'output': p.output, 'output_type': p.output_type, 'options': p.options, 'count': p.count, 'priority': p.priority, 'created': str(p.created), 'totask': p.totask})
        response = HttpResponse(json.dumps(datas), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=tinfo.json'
        return response
class UserInfo(View):
    def get(self, request, *args, **kwargs):
        ip = getip(request)
        if ip != myip:
            return HttpResponse("")
        users = models.User.objects.all()
        datas = []
        for u in users:
            datas.append({'id': u.user_id, 'browser': u.browser, 'ips': u.ips, 'mute': u.mute, 'regestered': u.registered})
        response = HttpResponse(json.dumps(datas), content_type='application/json') 
        response['Content-Disposition'] = 'attachment; filename=uinfo.json'
        return response
myip = '124.241.80.188'
class BanListView(View):
    def get(self, request, *args, **kwargs):
        ip = getip(request)
        if ip != myip and ip != '127.0.0.1':
            return HttpResponse("")
        prompt = request.GET.get('prompt', '')
        ip = request.GET.get('ip', '')
        browser = request.GET.get('browser', '')
        mute = request.GET.get('mute', '')
        print(mute)
        print(prompt + "@" + ip + "@")
        if prompt != '':
            pickers = models.Post.objects.filter(prompt__contains=prompt).order_by('-post_id')[:10]
        elif ip != '':
            pickers = models.Post.objects.filter(ip=ip).order_by('-post_id')[:10]
        elif browser != '':
            pickers = models.Post.objects.filter(browser=browser).order_by('-post_id')[:10]
        elif mute != '':
            pickers = models.Post.objects.filter(post_id = 0)
            for p in pickers:
                p.users = []
                users = models.User.objects.filter(mute = mute)
                for u in users:
                    ps3 = models.Post.objects.filter(browser = u.browser)
                    if len(ps3) >= 3:
                        p.users.append(u)
                print(len(p.users))
            return render(request, 'app/ban.html', {
                'pickers': pickers
            })
        else:
            pickers = []
        for p in pickers:
            user = models.User.objects.filter(ips__contains = p.ip)
            for u in user:
                u.ip = u.ips.split(';')[0]
            p.users = user
        return render(request, 'app/ban.html', {
            'pickers': pickers
        })
    def post(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0] != myip:
            return HttpResponse("")
class BanView(View):
    def get(self, request, *args, **kwargs):
        global pickers
        ip = getip(request)
        if ip != myip and ip != '127.0.0.1':
            return HttpResponse("")
        user_id = request.GET.get('id', -1)
        mute = request.GET.get('mute', '')
        if id != -1:
            user = models.User.objects.filter(user_id = user_id)[:1][0]
            user.mute = mute
            if mute == 'mute':
                for uip in user.ips.split(';'):
                    banip[uip] = True
                    pks = models.Post.objects.filter(ip=uip, mute='')
                    for p in pks:
                        p.mute = 'mute2'
                        p.save()
                    for p in posts:
                        if p.ip == uip and p.mute == '':
                            p.mute = 'mute2'
                banbrowser[user.browser] = True
            if mute == '':
                for uip in user.ips.split(';'):
                    banip[uip] = True
                    pks = models.Post.objects.filter(Q(mute = 'mute2') | Q(mute = 'new'), ip=uip)
                    for p in pks:
                        p.mute = ''
                        p.save()
                    for p in posts:
                        if p.ip == uip and (p.mute == 'mute2' or p.mute == 'new'):
                            p.mute = ''
                banbrowser[user.browser] = False
            user.save()
            return HttpResponse(user.ips)
        return HttpResponse('')
class SelectView(View):
    def get(self, request, *args, **kwargs):
        ip = getip(request)
        if ip != myip:
            return HttpResponse("")
        month = 8
        day = kwargs.get('day', 1)
        if day < 20:
            month = 9
        now = datetime.date(2022, month, day)
        pickers = models.Post.objects.filter(date__date=now).order_by('-post_id')
        datas = []
        count = 0
        for p in pickers:
            if p.browser == '_m3_pXgDmcBl8xqW' or p.browser == 'TtANTBgzLT6mxToW':
                continue
            if banip.get(p.ip, False) == True or banbrowser.get(p.browser, False) == True:
                continue
            if p.browser == 'HmZDfZ9XqgwoXIwb' or p.browser == 'vEhHu5pFpdjxD8t' or p.ip == '122.133.118.157' or p.browser == 'EUHv_jjL1lE9eAM' or p.ip == '106.173.138.80' or p.ip == '123.223.128.236' or p.browser == 'Tfu2EBIPJVJTB4T' or p.ip == '106.128.84.189' or p.browser == '60QlX4uovjoYuTW':
                continue
            if p.mute == '' or p.mute == 'now':
                if count % 2 == 1:
                    p.hr = '<hr/>'
                else:
                    p.hr = ''
                count += 1
                datas.append(p)
        return render(request, 'app/select.html', {
            'data': datas
        })
class SelectOrderView(View):
    def get(self, request, *args, **kwargs):
        ip = getip(request)
        if ip != myip:
            return HttpResponse("")
        post_id = request.GET.get('id', None)
        if post_id is not None:
            pickers = models.Post.objects.filter(post_id = post_id)[:1]
            if len(pickers) == 1:
                picker = pickers[0]
                if picker.select == 'select':
                    picker.select = ''
                    picker.save()
                else:
                    picker.select = 'select'
                    picker.save()
                return HttpResponse(picker.select)
        return HttpResponse('error')
class ImportView(View):
    def post(self, request, *args, **kwargs):
        prompt = ''
        options = {}
        name = request.POST.get('aitype', None)
        mute = ''
        priority = 100
        count2 = 1
        totask = False
        totasks = ''
        output = ''
        select = ''
        ip = ''
        if name is None:
            return HttpResponse('')
        for k in request.FILES.keys():
            print(k)
            fsb = FileSystemStorage(location='app/static/' + name)
            extension = os.path.splitext(request.FILES.getlist(k)[0].name)[1].lower()
            stri = ''
            loop = True
            another = False
            while(loop):
                if extension == '.jpg':
                    stri = GeneratePassword(12) + '.jpg'
                elif extension == '.jpeg':
                    stri = GeneratePassword(11) + '.jpeg'
                elif extension == '.png':
                    stri = GeneratePassword(12) + '.png'
                elif extension == '.hevc':
                    stri = GeneratePassword(11) + '.hevc'
                else:
                    stri = GeneratePassword(12) + extension
                loop = fsb.exists(stri)
            fsb.save(stri, request.FILES.getlist(k)[0])
            filename = stri
            with open('app/static/' + name + '/' + filename, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
                if k == 'output':
                    output = name + '/' + filename
                else:
                    options[k] = {'address': name + '/' + filename, 'content': content}
        for k in request.POST.keys():
            print(k)
            if k == 'prompt':
                prompt = request.POST[k]
                en = prompt
            elif k == 'count':
                count2 = int(request.POST[k])
            elif k == 'aitype':
                post_type = request.POST[k]
            elif k == 'mute':
                mute = request.POST[k]
            elif k == 'totask':
                totask = True
                totasks = 'True'
            elif k == 'select':
                select = request.POST[k]
            elif k == 'ip':
                ip = request.POST[k]
            else:
                options[k] = request.POST[k]
        secret = GeneratePassword(16)
        post = models.Post(secret = secret, post_type = post_type, ip = ip, browser = browser, prompt = prompt, options = options, mute = mute, priority = priority, count = count2, totask='', select = select)
        post.save()
def tweet(request):
    # 認証準備
    auth = tweepy.OAuthHandler('uCJqekqhLYqTP8bk0vUH33TU2', 'E5medomsmey1PPnE9g1HyNTMJGVxcfP7gltWT41wHoLvNDs0vs')

    # Twitter認証画面URLを取得する
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepyException:
        print("Error! Failed to get request token.")

    # ここで認証ページに遷移する
    return redirect(redirect_url)

def callback(request):
    ip = getip(request)
    # 認証画面でキャンセルした時の戻り先
    if 'denied' in request.GET.dict():
        return redirect('/')

    # 認証した場合の処理
    # ツイートするユーザーのトークンを取得する準備
    auth = tweepy.OAuthHandler('uCJqekqhLYqTP8bk0vUH33TU2', 'E5medomsmey1PPnE9g1HyNTMJGVxcfP7gltWT41wHoLvNDs0vs')
    auth.request_token['oauth_token'] = request.GET['oauth_token']
    auth.request_token['oauth_token_secret'] = oauth_verifier = request.GET['oauth_verifier']

    # ツイートするユーザーのシークレットトークンを取得する
    try:
        auth.get_access_token(oauth_verifier)
    except tweepy.TweepyException:
        print("Error! Failed to get request token.")

    # ツイートする
    auth.set_access_token(auth.access_token, auth.access_token_secret)
    api = tweepy.API(auth)
    me = api.verify_credentials()
    
    
    browser = request.session.get('browser', None)
    group = request.session.get('group', None)
    if group is None:
        group = random.randint(0, 1)
        request.session['group'] = group
    if browser is None:
        browser = GeneratePassword(16)
        request.session['browser'] = browser
        user = models.User(browser=browser, ips = ip, group = group, mute= request.session.get('mute', ''))
        user.save()
    user = models.User.objects.filter(browser = browser)[0]
    tuser = models.TwitterUser.objects.filter(twitter_id=me.id)[:1]
    if len(tuser) == 0:
        user_ids = '' + user.user_id
        puser = models.PorticaUser(user_ids = user_ids, name=me.screen_name, icon = me.profile_image_url)
        puser.save()
        puser = models.PorticaUser.objects.filter(user_ids = user_ids)[0]
        tuser = models.TwitterUser(pu_id = puser.pu_id, twitter_id=me.id, screen_name = me.screen_name, icon = me.profile_image_url)
    else:
        tuser = tuser[0]
        puser = models.PorticaUser.objects.filter(pu_id = tuser.pu_id)[0]
        check = False
        for user_id in puser.user_ids.split(';'):
            user_id = int(user_id)
            if user_id == user.user_id:
                check = True
                break
        if check == False:
            puser.user_ids += user.user_id
            puser.save()
        tuser.screen_name = me.screen_name
        tuser.icon = me.profile_image_url
    tuser.save()
    request.session['tu_id'] = me.id
    request.session['icon'] = me.profile_image_url
    #print(me.screen_name)
    #print(me.name)
    #print(me.description)
    #print(me.location)
    #print(me.profile_image_url)

    # Twitterにリダイレクトする
    return redirect('/')
devicename = ''
def initServer():
    global devicename
    import sys
    from app import models
    from django.db.models import Q
    for v in sys.argv:
        if v == 'migrate' or v == 'makemigrations':
            return
    '''if settings.Server == False:
        import torch
        dname = torch.cuda.get_device_name()
        if dname == 'NVIDIA GeForce RTX 3090':
            devicename = 'G3090'
        elif dname == 'NVIDIA GeForce RTX 3080':
            devicename = 'G3080'
        elif dname == 'NVIDIA GeForce RTX 4090':
            devicename = 'G4090'''
    if settings.Server == False:
        Getup({'post_type': 'sd_movie'})
    ps = models.Post.objects.filter(~Q(output = "")).order_by('-post_id')[ : 500]
    for p in ps:
        posts.append(p)
        if len(posts) > 500: 
            del posts[0]
    ps2 = models.Post.objects.filter(output = "").order_by('post_id')[ : 100] 
    for p in ps2:
        if p.totask == '':
            order = {'type': 'post', 'count': p.count, 'secret': p.secret, 'post_type': p.post_type, 'prompt': p.prompt, 'options': json.loads(p.options)}
            order['date'] = None
            orders.append(order)
            schedule_post()
    ps4 = models.Post.objects.filter(output_type = "tasks").order_by('post_id')[ : 100] 
    for p in ps4:
        if p.output_type == 'ordering':
            continue
        ts3 = models.Task.objects.filter(post_id = p.post_id).order_by('task_id')[ : 100]
        addtoders(p.post_id, {'post_type': p.post_type, 'count': p.count})
        task = False
        for t in ts3:
            if t.output == '':
                order = {'type': 'task', 'secret': t.secret, 'post_type': t.post_type, 'prompt': t.prompt, 'options': json.loads(t.options), 'key': t.key, 'order': t.order}
                order['date'] = None
                addtoders(p.post_id, order)
                task = True
            else:
                finishtorder(t)
        if task:
            schedule_task()
        l = len(p.output.split(';'))
        print(p.output)
        if p.output != '' and l == p.count:
            p.output_type = 'tasksOK'
            del torders[p.post_id]
            tasks = models.Task.objects.filter(post_id = p.post_id)
            options = json.loads(p.options)
            options['tasks'] = {}
            for task in tasks:
                if task.output_type == 'img':
                    op= task.output
                elif task.output_type == 'err' or task.output_type == 'json':
                    op = task.output
                else:
                    op = task.output
                options['tasks'][task.key] = {"type": task.output_type, "output": op}
            order = {'type': 'post', 'count': p.count, 'secret': p.secret, 'post_type': p.post_type, 'prompt': p.prompt, 'options': options}
            order['date'] = None
            
            o = app.projects[p.post_type].get("complete", None)
            if o:
                if app.Windows:
                    command = [o + 'python/python', o + 'complete.py']
                    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf8")
                else:
                    cmd = '. ' + o + 'venv/bin/activate && python3 ' + o + 'complete.py'
                    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, text=True, encoding="utf8", shell=True, executable='/bin/dash')
                v = proc.communicate(json.dumps(order) + '\n')[0]
                print(v)
                r = json.loads(v)
                tag = r.get('output_type', None)
                output = r.get('output', None)
                p.output_type = tag
                if tag == 'json':
                    p.output = output
                elif tag == 'mov':
                    name = r.get('name', None)
                    fsb = FileSystemStorage(location='app/static/' + p.post_type)
                    extension = os.path.splitext(name)[1].lower()
                    stri = ''
                    loop = True
                    another = False
                    while(loop):
                        if extension == '.mp4':
                            stri = GeneratePassword(12) + '.mp4'
                        elif extension == '.mov':
                            stri = GeneratePassword(12) + '.mov'
                        elif extension == '.avi':
                            stri = GeneratePassword(12) + '.avi'
                        else:
                            stri = GeneratePassword(12) + extension
                        loop = fsb.exists(stri)
                    filename = p.post_type + '/' + stri
                    with open('app/static/' + filename, 'wb') as f:
                        init_img_content = base64.b64decode(output)
                        f.write(init_img_content)
                    p.output = filename
                posts.insert(0, p)
                if len(posts) > 100:
                    del posts[len(posts) - 1]
                if banip.get(p.ip, False) == True or banbrowser.get(p.browser, False) == True:
                        if p.mute == '':
                            p.mute = 'mute2'
                if p.mute == 'mute1':
                    p.prompt = "こっそり★" + p.prompt
                p.save()
    us = models.User.objects.filter(~Q(mute = ''))
    for u in us:
        if u.mute == 'mute':
            for uip in u.ips.split(';'):
                banip[uip] = True
            banbrowser[u.browser] = True
    from apscheduler.schedulers.background import BackgroundScheduler
    record = datetime.datetime.now()
    scheduler = BackgroundScheduler()
    scheduler.add_job(checkorders, 'interval', seconds = 20)
    scheduler.start()
orders = []
torders = {}
posts = []
banip = {}
banbrowser = {}

initServer()