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

# jsfile, output, params, pymodname, comment
init_tasks = {
    u'港股深度数据挖掘' : ['getstocklist.js', 'stocklist.html', {}, 'parse_stocklist', '获取当日全部港股代码'],
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
                flog.write('>>>>> %s %s\n' % (self.comment, self.jsfile if self._runjs else self.pyfile + '.py'))
                flog.write(msg + '\n')

#    def finish(self):
#        '''如果py处理过程中没有错误发生，处理结束后删除html文件'''
#        if not self.error and self.htmlfile is not None:
#            os.remove(self.htmlfile)

    def addtask(self, subtask):
        '''动态添加子任务需要遵照 [jsfile, output, params, pymodname, comment] 格式'''
        if isinstance(subtask, list) and len(subtask) == 5:
            subtask += [self.name, 0]       #py文件返回5元素元组，需要添加2元素
            self.cb(subtask)
        else:
            print '子任务非法：', subtask

    def runjs(self, task):
        self.stdout = StringIO.StringIO()
        self.oldstdout, sys.stdout = sys.stdout, self.stdout
        self.jsfile, output, kwargs, self.pyfile, self.comment, self.name, self.retry_count = task
        kwargs['today'] = today
        self._runjs = True
        self.htmlfile = '%s/%s' % (today, output)
        print '>>>>>', self.comment, self.jsfile

        if not os.path.exists('./' + self.jsfile):
            self.onerror(u'脚本%s不存在' % self.jsfile)
            return

        self.retry = False
        command = ['casperjs', 'test', './' + self.jsfile, '--output=%s' % self.htmlfile] + ['--%s=%s' % (k, v) for k, v in kwargs.items()]
        command_str = '\t' + ' '.join(command) + '\n'
        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
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
#            self.finish()
        elif ret == 2:      #重试
            print '%s' % out#.decode('utf8')
        else:               #js执行成功，调用py
            print '%s' % out#.decode('utf8')
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
#            self.finish()

def spider_process():
    def addsubtask(task):
        sockp.send('', zmq.SNDMORE)
        sockp.send_pyobj(task)

    sockp = zmq.Context().socket(zmq.DEALER)
    sockp.connect(EndPoint)

    while True:
        task = sockp.recv_multipart()[-1]
        task = cPickle.loads(task)      #接收7元素元组
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
        addsubtask([ctx.name,])         #结束任务时给出任务名称，以便引擎正确判断任务是否结束

if __name__ == '__main__':
    ps, ts = [], {}
    if not os.path.exists(today):
        os.mkdir(today)
    elif os.path.exists(failog):
        os.remove(failog)

    sockm = zmq.Context().socket(zmq.DEALER)
    sockm.bind(EndPoint)

    for x in xrange(process_num):
        p = Process(target = spider_process)
        ps.append(p)
        p.start()

    for name, task in init_tasks.items():
        if ts.has_key(name):
            ts[name]['count'] += 1
        else:
            ts[name] = {'count' : 1, 'start' : clock()}
        task += [name, 0]       #init_tasks里面是5元素元组，添加2元素
        sockm.send('', zmq.SNDMORE)
        sockm.send_pyobj(task)

    while True:
        task = sockm.recv_multipart()
        subtask = cPickle.loads(task[-1])
        if len(subtask) > 1:
            name = subtask[-2]
            ts[name]['count'] += 1
            sockm.send('', zmq.SNDMORE)
            sockm.send_pyobj(subtask)
        else:
            name = subtask[0]
            ts[name]['count'] -= 1
            if ts[name]['count'] == 0:
                elapse = clock() - ts[name]['start']
                hours, minutes, seconds = elapse / 3600, (elapse % 3600) / 60, elapse % 60
                with loglock:
                    print '========== FINISH: %s >>> %dh %dm %ds ==========' % (name, hours, minutes, seconds)
                ts.pop(name)
                if len(ts) == 0:
                    for x in xrange(process_num):
                        sockm.send('', zmq.SNDMORE)
                        sockm.send_pyobj(None)
                    break

    for p in ps:
        p.join()
