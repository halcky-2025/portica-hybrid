import os
import shutil
import subprocess
from django.apps import AppConfig
import datetime
import json
import platform
Windows = False
if platform.system() == 'Windows':
    Windows = True
class MyAppConfig(AppConfig):
    name = 'app'
    verbose_name = "Portica"

    def ready(self):
        fds = os.listdir('./projects')
        dirs = [f for f in fds if os.path.isdir(os.path.join('projects', f))]
        for d in dirs:
            initProject(d)
        print(dirs)
        dirs = [f for f in fds if os.path.isdir(os.path.join('AI', f))]
        for d in dirs:
            initAI(d)
def initProject(name):
    todir = 'app/templates/' + name
    staticdir = 'app/templates/' + name
    frdir = 'projects/' + name + '/' + name + '/'
    with open(frdir + 'info.json', encoding="utf-8_sig") as f:
        projects[name] = json.loads(f.read())
        o = projects[name].get('order', None)
        prepare = projects[name].get('prepare', None)
        task = projects[name].get('task', None)
        complete = projects[name].get('complete', None)
        if o:
            if o == '..':
                projects[name]['order'] = frdir
            else:
                rets = o.split(':')
                projects[name]['order'] = rets[0] + '/' + rets[1] + '/' + rets[1] + '/'
                #initAI(rets[1])
        if prepare:
            if prepare == '..':
                projects[name]['prepare'] = frdir
            else:
                rets = prepare.split(':')
                projects[name]['prepare'] = rets[0] + '/' + rets[1] + '/' + rets[1] + '/'
                #initAI(rets[1])
        if task:
            if task == '..':
                projects[name]['task'] = frdir
            else:
                rets = task.split(':')
                projects[name]['task'] = rets[0] + '/' + rets[1] + '/' + rets[1] + '/'
                #initAI(rets[1])
        if complete:
            if complete == '..':
                projects[name]['complete'] = frdir
            else:
                rets = complete.split(':')
                projects[name]['complete'] = rets[0] + '/' + rets[1] + '/' + rets[1] + '/'
                #initAI(rets[1])
    if os.path.exists(todir) == False:
        if Windows:
            shutil.unpack_archive('python-3.9.13-embed-amd64.zip', frdir + 'python')
            with open(frdir + 'python/python39._pth') as f:
                data_lines = f.read()

            # 文字列置換
            data_lines = data_lines.replace("#import site", "import site")

            # 同じファイル名で保存
            with open(frdir + 'python/python39._pth', mode="w") as f:
                f.write(data_lines)
            command = [frdir + 'python/python', 'get-pip.py', '--no-warn-script-location']
            subprocess.run(command)
            command = [frdir + 'python/Scripts/pip3', 'install', '-r', frdir + 'requirements.txt', '--no-warn-script-location']
            subprocess.run(command)
        else:
            command = ['python3', '-m', 'venv', frdir + 'venv']
            subprocess.run(command)
            cmd = '. ' + frdir + 'venv/bin/activate && pip install -r ' + frdir + 'requirements.txt'
            subprocess.call(cmd, shell=True, executable='/bin/dash')
        os.mkdir(todir)
        if os.path.exists(staticdir) == False:
            os.mkdir(staticdir)
        todir += '/'
        if os.path.exists(frdir + 'input.html'):
            shutil.copy(frdir + 'input.html', todir)
        if os.path.exists(frdir + 'item.html'):
            shutil.copy(frdir + 'item.html', todir)
        if os.path.exists(frdir + 'description.html'):
            shutil.copy(frdir + 'description.html', todir)
        print('Copy:' + name)
def initAI(name):
    frdir = 'AI/' + name + '/' + name + '/'
    if os.path.exists(frdir + 'python/python') == False:
        if Windows:
            shutil.unpack_archive('python-3.9.13-embed-amd64.zip', frdir + 'python')
            with open(frdir + 'python/python39._pth') as f:
                data_lines = f.read()

            # 文字列置換
            data_lines = data_lines.replace("#import site", "import site")

            # 同じファイル名で保存
            with open(frdir + 'python/python39._pth', mode="w") as f:
                f.write(data_lines)
            command = [frdir + 'python/python', 'get-pip.py', '--no-warn-script-location']
            subprocess.run(command)
            command = [frdir + 'python/Scripts/pip3', 'install', '-r', frdir + 'requirements.txt', '--no-warn-script-location']
            subprocess.run(command)
        else:
            command = ['python3', '-m', 'venv', frdir + 'venv']
            subprocess.run(command)
            cmd = '. ' + frdir + 'venv/bin/activate && pip install -r ' + frdir + 'requirements.txt'
            subprocess.call(cmd, shell=True, executable='/bin/dash')
projects = {}