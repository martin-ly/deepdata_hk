#coding: utf8

import urllib2, deephk, re, sys
from bs4 import BeautifulSoup

def run(ctx, html, kwargs):
    url = 'http://www.hkexnews.hk/sdw/search/stocklist_c.asp?SortBy=StockCode&Lang=CHI&ShareholdingDate=' + kwargs['today']
    data = urllib2.urlopen(url).read()

    codes = getattr(sys.modules[__package__], "codes", [])
    bs = BeautifulSoup(data, 'html5lib', from_encoding='big5')

    trs = bs.find_all('tr', class_=re.compile(r'TableContentStyle\d{1}'))
    if len(trs) == 0:
        ctx.onerror(u'抓取的证券代码数量为0')
    count = 0
    for tr in trs:
        code = unicode(tr.find('td', align='Center').string).encode('utf8')
        name = unicode(tr.find('span').string)
        if len(code) != 5 or int(code) == 0:
            ctx.onerror(u'证券代码非法：%s' % code)
        else:
            if len(codes) != 0 and code not in codes:
                continue
            #ctx.addtask(['qszz.js', code + '_qszz.html', {'code' : code}, 30, 'qszz', u'%s - 券商追踪' % name])
            ctx.addtask([None, code + '_gfjm.html', {'code' : code}, 300, 'gfjm_v2', u'%s - 股份解码' % name])
