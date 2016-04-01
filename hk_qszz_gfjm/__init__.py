#coding: utf8

import parse_stocklist
import gfjm_main
import gfjm_end
import qszz
import time, os
from main import OUTPUT

today = time.strftime('%Y%m%d')
path = __path__[0] + '/' + today
if not os.path.exists(path):
    os.mkdir(path)

jsfile = 'getstocklist.js'
jstimeout = 30
output = 'stocklist.html'
params = {}
pymodname = 'parse_stocklist'
description = u'获取当日全部港股代码'
finalinvoke = ['hkexe/DeepSecurityMaster.exe', '-d', OUTPUT.FOLDER, '-t', '0x01']
finaltimeout = 36000
finalencoding = 'gbk'
