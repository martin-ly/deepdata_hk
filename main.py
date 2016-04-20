#!/usr/bin/env python
#coding: utf-8

'''
程序分为两个部分：网页抓取部分和页面解析部分，main.py把两部分脚本串联在一起，相当于驱动引擎。

引擎从settings.py中读取爬虫的初始设置。

网页抓取部分可以由casperjs，也可以由python程序完成，页面解析部分现在是由python程序独立完成的。

js代码中，脚本获得html页面后需要将其写入磁盘文件中供py脚本使用，echo到concole的信息，包括爬取页面过程中
的异常信息，都会被main.py获得，脚本在最后返回OK时，表示获取html成功。main将调用对应的py模块的run方法来
解析js输出的html文件。否则表示获取html失败，全部输出将被记录日志。

ContextJS是引擎的核心类，每个ContextJS实例都是一个爬虫数据抓取和解析的任务，它包含以下重要方法：
run: 启动爬虫，该方法将首先调用网页抓取部分，然后根据抓取结果来决定是否调用页面解析部分
onerror: py脚本调用该方法向引擎报告错误信息，该信息会记录在错误日志中，但是脚本会继续运行
onfinish: 任务结束时调用该方法来删除临时文件
addtask: py脚本调用该方法向引擎增加一个新的爬虫任务

编码格式：py和js脚本必须使用utf8编码，py脚本输出的字符串必须是unicode编码
'''

import subprocess, time, os, sys, traceback, zmq, cPickle, StringIO
from time import clock
from threading import Thread
from multiprocessing import Process, Lock
from settings import *

ThreadStop = Thread._Thread__stop

today = time.strftime('%Y%m%d')
failog = os.getcwd() + '/log/%s.log' % today
loglock = Lock()
EndPoint = 'tcp://127.0.0.1:9066'

class ContextJS(Thread):
    def __init__(self, pkgname, cb, task):
        Thread.__init__(self)
        self.pkgmod = __import__(pkgname)
        self.cb, self.error, self.subtasks = cb, False, []
        self.task = task

    def onerror(self, msg, err = True):
        ''' 输出已经被重定向
        msg: 接收unicode编码
        '''
        self.error = err
        if DEBUG:
            msg = '[PID=%d] ' % os.getpid() + msg
        try:
            #print msg.encode(terminal_charset, 'xmlcharrefreplace')
            print msg
        except:
            msg = '+++++\n\n' + traceback.format_exc() + '\n+++++\n'
            print msg

        if err or DEBUG:
            with loglock:
                with open(failog, 'a+') as flog:
                    flog.write('>>>>> [%d] %s %s\n' % (int(self.retry_count), self.comment.encode('utf8'), self.jsfile if self._runjs else self.pyfile + '.py'))
                    flog.write(msg.encode('utf8') + '\n')

    def onfinish(self, files):
        '''删除子任务产生的临时文件'''
        for f in files:
            if os.path.exists(f):
                os.remove(f)

    def addtask(self, subtask):
        '''动态添加子任务需要遵照 [jsfile, output, params, jstimeout, pymodname, comment] 格式
        jsfile: js文件名，包含扩展名
        output: js输出的网页文件名，注意：脚本可以直接使用这个文件名，也可以由js脚本和py脚本双方协商文件名规则
        params: 任务参数，自定义，引擎会在参数中加上today，表示执行日期，格式为yyyymmdd
        jstimeout: js脚本执行超时时间，单位为秒，超过时间将杀死casperjs进程
        pymodname: js脚本执行完成后，需要调用的py脚本
        comment: 任务说明，显示用
        '''
        if isinstance(subtask, list) and len(subtask) == 6:
            subtask += [self.bbname, 0]       #py文件返回6元素元组，需要添加2元素
            self.cb(subtask)
        else:
            print u'子任务非法：', subtask

    def safe_print(self, msg):
        with loglock:
            print >> self.oldstdout, msg

    def _stop(self):
        if self.isAlive():
            ThreadStop(self)

    def run(self):
        self._runjs = True
        self.jsfile, output, kwargs, jstimeout, self.pyfile, self.comment, self.bbname, self.retry_count = self.task
        kwargs['today'] = today
        if DEBUG:
            with loglock:
                print u'>>>>> [PID=%d][RETRY=%d] %s, params = %s' % (os.getpid(), int(self.retry_count), self.jsfile, kwargs)

        self.stdout = StringIO.StringIO()
        self.oldstdout, sys.stdout = sys.stdout, self.stdout

        if not DEBUG:
            self.onerror(u'>>>>> [%d] %s %s' % (int(self.retry_count), self.comment, self.jsfile if self._runjs else self.pyfile + '.py'), False)

        self.htmlfile = '%s/%s' % (today, output)
        out, self.retry = ['OK',], False

        ### 执行js脚本 ###

        if self.jsfile is not None:
            if not os.path.exists('./' + self.jsfile):
                self.onerror(u'脚本%s不存在' % self.jsfile)
                return

            command = ['casperjs', 'test', './' + self.jsfile, '--output=%s' % self.htmlfile] + ['--%s="%s"' % (k, v) for k, v in kwargs.items()]
            command_str = '\t' + ' '.join(command) + '\n'

            p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            deadline = time.time() + jstimeout
            while time.time() < deadline and p.poll() == None:
                time.sleep(0.01)
            if p.poll() == None:
                p.kill()
                print u'超时'

            out, _ = p.communicate()
            out = command_str + out
            out = out.split('\n')
            if len(out) == 1:
                out.append('未知执行结果，按失败处理')
            out = [l.strip() for l in out if len(l.strip()) > 0]

        ### js执行完成，下面执行与js相关的py来解析网页 ###
        ### out: utf8编码 ###

        #0-成功,1-失败,2-重试,3-不需要调用py
        if out[-1] == 'OK' or (len(out) >= 2 and out[-2] == 'OK'):
            ret = 0
        elif out[-1] == 'PASS' or (len(out) >= 2 and out[-2] == 'PASS'):
            ret = 3
        else:
            self.retry = True
            self.retry_count += 1
            if self.retry_count < retry_num:
                ret = 2
            else:
                ret = 1
        out = '\n'.join(out)

        if ret == 1:        #js执行失败，写入失败日志备查
            self.onerror(out.decode('utf8'))

        elif ret in [2, 3]: #重试 and 成功，但是不需要调用py
            self.onerror(out.decode('utf8'), False)

        else:               #js执行成功，调用py
            self.onerror(out.decode('utf8'), False)
            self._runjs = False
            mod = getattr(self.pkgmod, self.pyfile, None)
            if mod is None:
                self.onerror(u'Module: %s not found in Package: %s' % (self.pyfile, self.pkgmod.__name__))
            else:
                run = getattr(mod, 'run', None)
                if run is None:
                    self.onerror(u'模块中找不到run方法')
                else:
                    try:
                        run(self, '%s/%s' % (today, output), kwargs)
                    except:
                        self.retry = True
                        self.retry_count += 1
                        ret = traceback.format_exc()
                        self.onerror(ret.decode('utf8'))

def spider_process():
    def addsubtask(task):
        if isinstance(task, list) and len(task) == 8:
            task.append(pkgname)
        sockp.send_pyobj(task)

    orign_path = os.getcwd()
    sockp = zmq.Context().socket(zmq.DEALER)
    sockp.setsockopt(zmq.IDENTITY, '%d' % os.getpid())
    sockp.connect(EndPoint)
    addsubtask('checkin')

    while 1:
        os.chdir(orign_path)
        task = sockp.recv_multipart()[-1]
        task = cPickle.loads(task)      #接收9元素元组

        pkgname = task[-1]
        os.chdir(pkgname)
        task = task[:-1]

        ctx = ContextJS(pkgname, addsubtask, task)
        ctx.start()
        ctx.join(task[3])

        if ctx.isAlive():
            ctx._stop()
            ctx.retry = True
            ctx.retry_count += 1
            ctx.onerror(u'任务超时', False if ctx.retry_count < retry_num else True)

        sys.stdout = ctx.oldstdout
        with loglock:
            try:
                print ctx.stdout.getvalue().encode(terminal_charset, 'xmlcharrefreplace')
            except:
                msg = '+++++\n\n' + traceback.format_exc() + '\n+++++\n'
                print msg
        if ctx.retry and ctx.retry_count < retry_num:
            task[-1] = ctx.retry_count
            addsubtask(task)
        if len(task) == 8:
            task.append(pkgname)
        addsubtask(('finished', task))         #结束任务

def OnNewTask(sockm, queue, waitingps, task):
    try:
        p = waitingps.pop(0)
    except:
        queue.append(task)
    else:
        sockm.send('%d' % p.pid, zmq.SNDMORE)
        sockm.send_pyobj(task)

def OnTaskFinished(cmd, timeout):
    ''' 启动后置任务并在后置任务超时后杀死，后置任务自己管理输出和日志
    cmd: __init__.py中预置的finalinvoke
    timeout: __init__.py中预置的finaltimeout
    '''
    begin = clock()
    p = subprocess.Popen(cmd, shell = True)
    deadline = time.time() + timeout
    while time.time() < deadline and p.poll() == None:
        time.sleep(0.01)
    if p.poll() == None:
        print u'超时'
        p.kill()

    msg = '\n%s\nExecuted %.2f Seconds.\n' % (cmd, clock() - begin)
    with loglock:
        print msg
        with open(failog, 'a+') as flog:
            flog.write(msg.encode('utf8'))

if __name__ == '__main__':
    runmode = 0         #不带参数，表示按照settings.py里面定义来运行
    if len(sys.argv) > 1:
        runid = sys.argv[-1].lower()
        if runid == 'all':
            runmode = 1         #all参数，无视init_tasks.enable，全部运行
        else:
            runmode = 2

    if not os.path.exists('log'):
        os.mkdir('log')

    ps, ts, finishts = {}, {}, []
    queue, waitingps = [], []  #待机任务，待机进程

    sockm = zmq.Context().socket(zmq.ROUTER)
    sockm.bind(EndPoint)

    for x in xrange(process_num):
        p = Process(target = spider_process)
        p.start()
        ps[p.pid] = p

    for taskid, task in init_tasks.items():
        name = task['description']
        pkgname = task['package']
        enable = task.get('enable', False)
        if runmode == 0 and enable == False:
            continue
        if runmode == 2 and str(taskid) != runid:
            continue

        if ts.has_key(name):
            ts[name]['count'] += 1
        else:
            ts[name] = {'count' : 1, 'start' : clock()}

        _mod = __import__(pkgname)
        task = [_mod.jsfile, _mod.output, _mod.params, _mod.jstimeout, _mod.pymodname, _mod.description, name, 0, pkgname]
        ts[name]['final_invoke'] = getattr(_mod, 'finalinvoke', None)
        ts[name]['final_timeout'] = getattr(_mod, 'finaltimeout', 60)
        with loglock:
            with open(failog, 'a+') as flog:
                flog.write('===== Task %s Begin at %s =====\n' % (name.encode('utf8'), time.strftime('%H:%M:%S')))
        OnNewTask(sockm, queue, waitingps, task)

    while 1:
        pid, task = sockm.recv_multipart()
        task = cPickle.loads(task)
        if isinstance(task, str) and task == 'checkin':     #工作进程签到
            try:
                task = queue.pop(0)
            except:
                p = ps.get(int(pid), None)
                if p:
                    waitingps.append(p)
            else:
                sockm.send(pid, zmq.SNDMORE)
                sockm.send_pyobj(task)

        elif isinstance(task, list):                 #新的子任务
            name = task[-3]
            ts[name]['count'] += 1
            OnNewTask(sockm, queue, waitingps, task)

        else:                       #子任务完成
            word, t = task
            try:
                next_task = queue.pop(0)
            except:
                p = ps.get(int(pid), None)
                if p:
                    waitingps.append(p)
            else:
                sockm.send(pid, zmq.SNDMORE)
                sockm.send_pyobj(next_task)

            jsfile, _, kwargs, _, pyfile, _, name, _, pkgname = t
            ts[name]['count'] -= 1
            if ts[name]['count'] > 0:
                with loglock:
                    print '=== [%s:%s], args %s' % (jsfile, pyfile, str(kwargs))
                    print '=== %s: %d task(s) left.\n' % (name, ts[name]['count'])
            else:
                elapse = clock() - ts[name]['start']
                hours, minutes, seconds = elapse / 3600, (elapse % 3600) / 60, elapse % 60
                with loglock:
                    print '========== FINISH: %s >>> %dh %dm %ds ==========' % (name, hours, minutes, seconds)
                    with open(failog, 'a+') as flog:
                        flog.write('========== FINISH: %s >>> %dh %dm %ds ==========\n' % (name.encode('utf8'), hours, minutes, seconds))

                if ts[name]['final_invoke']:
                    t = Thread(target = OnTaskFinished, args = (ts[name]['final_invoke'], ts[name]['final_timeout']))
                    finishts.append(t)
                    t.start()

                ts.pop(name)
                if len(ts) == 0:
                    break

    for _, p in ps.iteritems():
        p.terminate()

    for t in finishts:
        t.join()
