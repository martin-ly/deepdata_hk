#!/usr/bin/env python
#coding: utf-8

'''
程序分为两个部分：js代码负责抓取网页，py脚本负责解析页面，main.py把两部分脚本串联在一起，相当于驱动引擎。

js代码中，脚本获得html页面后需要将其写入磁盘文件中供py脚本使用，echo到concole的信息，包括爬取页面过程中
的异常信息，都会被main.py获得，脚本在最后返回OK时，表示获取html成功。main将调用对应的py模块的run方法来
解析js输出的html文件。否则表示获取html失败，全部输出将被记录日志。

py脚本的run方法可以调用ctx.onerror返回解析失败信息，该信息会记录在错误日志中，但是脚本会继续运行，调用
ctx.runjs可以从py脚本中调用js脚本继续抓取工作。

编码格式：py和js脚本必须使用utf8编码
'''

import subprocess, time, os, sys, traceback, zmq, cPickle, StringIO
from time import clock
from multiprocessing import Process, Lock

today = time.strftime('%Y%m%d')
failog = '%s/fail.log' % today
process_num, retry_num = 10, 5     #爬虫进程数量，失败重试次数
loglock = Lock()
EndPoint = 'tcp://127.0.0.1:9066'

# jsfile, output, params, jstimeout, pymodname, comment
init_tasks = {
    u'港股深度数据挖掘' : ['getstocklist.js', 'stocklist.html', {}, 30, 'parse_stocklist', '获取当日全部港股代码'],
}

class ContextJS:
    def __init__(self, cb):
        self.cb, self.error, self.subtasks = cb, False, []

    def onerror(self, msg):
        self.error = True
        try:
            print msg
        except Exception, e:
            msg = '*****************************************\n' + msg + '\n*****************************************'
            print msg
        with loglock:
            with open(failog, 'a+') as flog:
                flog.write('>>>>>[%d] %s %s\n' % (int(self.retry_count), self.comment, self.jsfile if self._runjs else self.pyfile + '.py'))
                flog.write(msg + '\n')

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
            subtask += [self.name, 0]       #py文件返回6元素元组，需要添加2元素
            self.cb(subtask)
        else:
            print '子任务非法：', subtask

    def runjs(self, task):
        self.stdout = StringIO.StringIO()
        self.oldstdout, sys.stdout = sys.stdout, self.stdout
        self.jsfile, output, kwargs, jstimeout, self.pyfile, self.comment, self.name, self.retry_count = task
        kwargs['today'] = today
        self._runjs = True
        self.htmlfile = '%s/%s' % (today, output)
        print '>>>>>[%d]' % (int(self.retry_count)+1,), self.comment, self.jsfile

        if not os.path.exists('./' + self.jsfile):
            self.onerror(u'脚本%s不存在' % self.jsfile)
            return

        self.retry = False
        command = ['casperjs', 'test', './' + self.jsfile, '--output=%s' % self.htmlfile] + ['--%s=%s' % (k, v) for k, v in kwargs.items()]
        command_str = '\t' + ' '.join(command) + '\n'

        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        deadline = time.time() + jstimeout
        while time.time() < deadline and p.poll() == None:
            time.sleep(0.01)
        if p.poll() == None:
            print '超时'
            p.kill()

        out, _ = p.communicate()
        out = command_str + out
        out = out.split('\n')
        if len(out) == 1:
            out.append('未知执行结果，按失败处理')
        out = [l.strip() for l in out if len(l.strip()) > 0]

        #0-成功,1-失败,2-重试
        if out[-1] == 'OK' or out[-2] == 'OK':
            ret = 0
        else:
            self.retry = True
            self.retry_count += 1
            if self.retry_count < retry_num:
                ret = 2
            else:
                ret = 1
        out = '\n'.join(out)

        if ret == 1:        #js执行失败，写入失败日志备查
            self.onerror(out)
        elif ret == 2:      #重试
            print '%s' % out
        else:               #js执行成功，调用py
            print '%s' % out
            self._runjs = False
            try:
                mod = __import__(self.pyfile)
            except ImportError, e:
                self.onerror(e.message)
            else:
                run = getattr(mod, 'run', None)
                if run is None:
                    self.onerror('模块中找不到run方法')
                else:
                    try:
                        run(self, '%s/%s' % (today, output), kwargs)
                    except:
                        ret = traceback.format_exc()
                        self.onerror(ret)

def spider_process():
    def addsubtask(task):
        sockp.send_pyobj(task)

    sockp = zmq.Context().socket(zmq.DEALER)
    sockp.setsockopt(zmq.IDENTITY, '%d' % os.getpid())
    sockp.connect(EndPoint)
    addsubtask('checkin')

    while True:
        task = sockp.recv_multipart()[-1]
        task = cPickle.loads(task)      #接收8元素元组
        if task is None:
            break
        ctx = ContextJS(addsubtask)
        ctx.runjs(task)
        sys.stdout = ctx.oldstdout
        with loglock:
            try:
                print ctx.stdout.getvalue().decode('utf8')
            except Exception, e:
                print '*****************************************\n'
        if ctx.retry and ctx.retry_count < retry_num:
            task[-1] = ctx.retry_count
            addsubtask(task)
        addsubtask(('finished', task))         #结束任务

def OnNewTask(sockm, queue, waitingps, task):
    try:
        p = waitingps.pop(0)
    except:
        queue.append(task)
    else:
        sockm.send('%d' % p.pid, zmq.SNDMORE)
        sockm.send_pyobj(task)

if __name__ == '__main__':
    ps, ts = {}, {}
    queue, waitingps = [], []  #待机任务，待机进程
    if not os.path.exists(today):
        os.mkdir(today)
    elif os.path.exists(failog):
        os.remove(failog)

    sockm = zmq.Context().socket(zmq.ROUTER)
    sockm.bind(EndPoint)

    for x in xrange(process_num):
        p = Process(target = spider_process)
        p.start()
        ps[p.pid] = p

    for name, task in init_tasks.items():
        if ts.has_key(name):
            ts[name]['count'] += 1
        else:
            ts[name] = {'count' : 1, 'start' : clock()}
        task += [name, 0]       #init_tasks里面是6元素元组，添加2元素
        OnNewTask(sockm, queue, waitingps, task)

    while True:
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
            name = task[-2]
            ts[name]['count'] += 1
            OnNewTask(sockm, queue, waitingps, task)

        else:                       #子任务完成
            try:
                next_task = queue.pop(0)
            except:
                p = ps.get(int(pid), None)
                if p:
                    waitingps.append(p)
            else:
                sockm.send(pid, zmq.SNDMORE)
                sockm.send_pyobj(next_task)

            task = task[-1]
            jsfile, _, kwargs, _, pyfile, _, name, _ = task
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
                ts.pop(name)
                if len(ts) == 0:
                    for pid, _ in ps.iteritems():
                        sockm.send('%d' % pid, zmq.SNDMORE)
                        sockm.send_pyobj(None)
                    break

    for _, p in ps.iteritems():
        p.join()
