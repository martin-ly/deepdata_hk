#coding: utf8

import re, sys, urllib2, cookielib
from bs4 import BeautifulSoup
sys.path.append('..')
from utils import *

def run(ctx, html, kwargs):
    codes = getattr(sys.modules[__package__], 'codes', None)
    cookie_fname = getattr(sys.modules[__package__], 'cookie_fname', None)

    path = '/sdw/search/stocklist_c.asp?SortBy=StockCode&Lang=CHI&ShareholdingDate=' + kwargs['today']
    data = GetUrl('http://www.hkexnews.hk', path)

    bs = BeautifulSoup(data, 'html5lib', from_encoding='big5')
    trs = bs.find_all('tr', class_=re.compile(r'TableContentStyle\d{1}'))
    if len(trs) == 0:
        ctx.onerror(u'抓取的证券代码数量为0')
    for tr in trs:
        code = unicode(tr.find('td', align='Center').string).encode('utf8')
        name = unicode(tr.find('span').string)
        if len(code) != 5 or int(code) == 0:
            ctx.onerror(u'证券代码非法：%s' % code)
        else:
            if codes is not None and code not in codes:
                continue
            ctx.addtask([None, code + '_qszz.html', {'code' : code}, 30, 'qszz_v2', u'%s - 券商追踪' % name])
            ctx.addtask([None, code + '_gfjm.html', {'code' : code}, 300, 'gfjm_v2', u'%s - 股份解码' % name])
