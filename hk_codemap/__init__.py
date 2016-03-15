#coding: utf8

import hkscc_participants
import time, os

today = time.strftime('%Y%m%d')
path = __path__[0] + '/' + today
if not os.path.exists(path):
    os.mkdir(path)

jsfile = None
jstimeout = 30
output = None
params = {}
pymodname = 'hkscc_participants'
description = '港股结算参与者'
