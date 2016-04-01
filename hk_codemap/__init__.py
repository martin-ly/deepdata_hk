#coding: utf8

import hkscc_participants
import check_participant
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
pymodname = 'hkscc_participants'
description = u'港股结算参与者'
finalinvoke = ['start', '/wait', 'hkexe/DeepSecurityMaster.exe', '-d', OUTPUT.FOLDER, '-t', '0x08']
finaltimeout = 60
finalencoding = 'gbk'
