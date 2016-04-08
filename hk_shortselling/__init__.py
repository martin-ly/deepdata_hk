#coding: utf8

import shortselling
import time, os
from main import OUTPUT

today = time.strftime('%Y%m%d')
path = __path__[0] + '/' + today
if not os.path.exists(path):
    os.mkdir(path)

jsfile = None
jstimeout = 30
output = None
params = {}
pymodname = 'shortselling'
description = u'港股市场沽空'
finalinvoke = ['start', '/wait', 'hkexe/DeepSecurityMaster.exe', '-d', OUTPUT.FOLDER, '-t', '0x04']
finaltimeout = 60
