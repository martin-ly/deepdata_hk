#coding: utf8

import parse_stocklist
import gfjm_main
import gfjm_end
import qszz
import getstocklist
import qszz_v2
import gfjm_v2
import time, os, sys

today = time.strftime('%Y%m%d')
path = __path__[0] + '/' + today
if not os.path.exists(path):
    os.mkdir(path)

#jsfile = 'getstocklist.js'
#pymodname = 'parse_stocklist'
jsfile = None
pymodname = 'getstocklist'

jstimeout = 30
output = 'stocklist.html'
params = {}
description = u'获取当日全部港股代码'
finalinvoke = ['start', '/wait', 'hkexe/DeepSecurityMaster.exe', '-d', os.path.join(os.path.dirname(__file__), today), '-t', '0x03']
finaltimeout = 36000

# 证券代码过滤，如果这里定义了代码，则只爬这些代码的数据，否则爬全部
#codes = ['00001']
