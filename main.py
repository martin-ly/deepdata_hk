#!/usr/bin/env python
#coding: utf-8

# js代码中，echo到concole的信息都会被main.py获得，必须在最后返回FAIL或OK，
# 如果返回FAIL，表示js代码获取html失败，将被记录日志，如果返回OK，表示获取
# html成功。main.py将调用对应的py模块的run方法来解析js输出的html文件，run
# 方法返回一个tuple，（-1, errmsg)表示解析失败，(0, new task list)表示调
# 用成功，解析脚本返回新的任务列表

import subprocess, time, os, sys, traceback

today = time.strftime('%Y%m%d')
failog = '%s/fail.log' % today

# jsfile, output, pymodname, comment
init_tasks = [
    ('getstocklist.js', 'stocklist.html', [], 'parse_stocklist', u'获取当日全部港股代码'),
]

class ContextJS:
    def __init__(self):
        self.jsfile, self.pyfile, self.comment = None, None, None

    def onerror(self, msg):
        with open(failog, 'a+') as flog:
            flog.write('>>>>> %s %s\n' % (self.comment.encode('utf8'), self.jsfile if self._runjs else self.pyfile))
            flog.write(msg.encode('utf8') + '\n')

    def runjs(self, task):
        newctx = ContextJS()
        newctx.jsfile, output, args, newctx.pyfile, newctx.comment = task
        newctx._runjs = True
        print '>>>>>', newctx.comment, newctx.jsfile

        if not os.path.exists('./' + newctx.jsfile):
            print u'脚本%s不存在' % newctx.jsfile
            newctx.onerror(u'脚本%s不存在' % newctx.jsfile)
            return

        command = ['casperjs', './' + newctx.jsfile, '--output=%s/%s' % (today, output)] + args
        p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, _ = p.communicate()
        if len(out) == 0:
            print '%s' % u'未知执行结果，按失败处理'
            newctx.onerror('%s' % u'未知执行结果，按失败处理')
            ret = False
        else:
            out = out.split('\n')
            if len(out) == 0:
                out.append(u'未知执行结果，按失败处理')

            while len(out[-1]) == 0:
                out = out[:-1]

            if out[-1] == 'FAIL':
                ret = False
            elif out[-1] == 'OK':
                ret = True
            else:
                out.append(u'未知执行结果，按失败处理')
                ret = False

            out = '\n'.join(out)
            print '%s' % out

        if not ret:       #js执行失败，写入失败日志备查
            newctx.onerror(out)
        else:   #js执行成功，调用py
            newctx._runjs = False
            try:
                mod = __import__(newctx.pyfile)
            except ImportError, e:
                print e.message
                newctx.onerror(e.message)
            else:
                run = getattr(mod, 'run', None)
                if run is None:
                    print u'模块中找不到run方法'
                    newctx.onerror(u'模块中找不到run方法')
                else:
                    try:
                        run(newctx, '%s/%s' % (today, output))
                    except:
                        ret = traceback.format_exc()
                        print ret
                        newctx.onerror(ret)

if __name__ == '__main__':
    if not os.path.exists(today):
        os.mkdir(today)
    elif os.path.exists(failog):
        os.remove(failog)
    for task in init_tasks:
        ctx = ContextJS()
        ctx.runjs(task)
    print '========== FINISHED!! =========='
