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

import subprocess, time, os, sys, traceback

today = time.strftime('%Y%m%d')
failog = '%s/fail.log' % today

# jsfile, output, params, pymodname, comment
init_tasks = [
    ('getstocklist.js', 'stocklist.html', {}, 'parse_stocklist', '获取当日全部港股代码'),
]

class ContextJS:
    def __init__(self):
        self.jsfile, self.pyfile, self.comment, self.error, self.htmlfile = None, None, None, False, None

    def onerror(self, msg):
        self.error = True
        print msg.decode('utf8')
        with open(failog, 'a+') as flog:
            flog.write('>>>>> %s %s\n' % (self.comment, self.jsfile if self._runjs else self.pyfile))
            flog.write(msg + '\n')

    def finish(self):
        '''如果py处理过程中没有错误发生，处理结束后删除html文件'''
        if not self.error and self.htmlfile is not None:
            os.remove(self.htmlfile)

    def runjs(self, task):
        newctx = ContextJS()
        newctx.jsfile, output, kwargs, newctx.pyfile, newctx.comment = task
        newctx._runjs = True
        newctx.htmlfile = '%s/%s' % (today, output)
        print '>>>>>', newctx.comment, newctx.jsfile

        if not os.path.exists('./' + newctx.jsfile):
            newctx.onerror('脚本%s不存在' % newctx.jsfile)
            return

        command = ['casperjs', 'test', './' + newctx.jsfile, '--output=%s' % newctx.htmlfile] + ['--%s=%s' % (k, v) for k, v in kwargs.items()]
        command_str = '\t' + ' '.join(command) + '\n'
        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, _ = p.communicate()
        out = command_str + out
        out = out.split('\n')
        if len(out) == 1:
            out.append('未知执行结果，按失败处理')
        while len(out[-1]) == 0:
            out = out[:-1]
        if out[-1] == 'OK' or out[-2] == 'OK':
            ret = True
        else:
            ret = False
        out = '\n'.join(out)

        if not ret:       #js执行失败，写入失败日志备查
            newctx.onerror(out)
        else:   #js执行成功，调用py
            print '%s' % out.decode('utf8')
            newctx._runjs = False
            try:
                mod = __import__(newctx.pyfile)
            except ImportError, e:
                newctx.onerror(e.message)
            else:
                run = getattr(mod, 'run', None)
                if run is None:
                    newctx.onerror('模块中找不到run方法')
                else:
                    try:
                        run(newctx, '%s/%s' % (today, output))
                    except:
                        ret = traceback.format_exc()
                        newctx.onerror(ret)
        newctx.finish()

if __name__ == '__main__':
    if not os.path.exists(today):
        os.mkdir(today)
    elif os.path.exists(failog):
        os.remove(failog)
    for task in init_tasks:
        ctx = ContextJS()
        ctx.runjs(task)
    print '========== FINISHED!! =========='
