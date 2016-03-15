#coding: utf8

import shortselling
import time, os

today = time.strftime('%Y%m%d')
path = __path__[0] + '/' + today
if not os.path.exists(path):
    os.mkdir(path)

jsfile = None
jstimeout = 30
output = None
params = {}
pymodname = 'shortselling'
description = '港股市场沽空'
