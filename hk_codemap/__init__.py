#coding: utf8

import hkscc_participants
import check_participant
import time, os

today = time.strftime('%Y%m%d')
path = __path__[0] + '/' + today
if not os.path.exists(path):
    os.mkdir(path)

#定义casperjs运行的js脚本，如果为None，表示直接调用后面的py脚本抓网页
jsfile = None
#js运行超时时间，秒，超时将被杀进程
jstimeout = 30
#js脚本输出文件名，任务并不严格使用该名称，两部分的数据交换文件名称可以自己协商
output = None
#初始调度参数，这些参数会传递给js脚本并最终传递给py脚本
params = {}
#py脚本名称，该脚本必须和__init__py位于同一个目录下，且在__init__.py中必须import该脚本，不能使用from ... import ...格式，也不能使用import ... as ...格式
pymodname = 'hkscc_participants'
#任务描述，unicode编码
description = u'港股结算参与者'
#该任务全部结束后，需要调用的后置程序，引擎调用该程序，但是不会捕获它的输出，也不会代替它处理日志
finalinvoke = ['start', '/wait', 'hkexe/DeepSecurityMaster.exe', '-d', os.path.join(os.path.dirname(__file__), today), '-t', '0x08']
#后置任务执行超时时间，秒，超过该时间引擎将杀死后置任务进程，不设置该项默认60秒
finaltimeout = 60
