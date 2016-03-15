#coding: utf8

import re, urllib2
from threading import Thread
from bs4 import BeautifulSoup

today = None

def gethtml(url, timeflag, block):
    '''
    timeflag: 0-上午，1-下午
    block: 0-创业板，1-主板
    '''
    html = urllib2.urlopen(url).read()
    bs = BeautifulSoup(html, 'html5lib', from_encoding='big5')
    pre = bs.find('pre')
    if not pre:
        ctx.onerror('找不到定位点pre')
        return

    fname = '%s/%s.%s.ss' % (today, u'main' if block == 1 else u'gem', u'morning' if timeflag == 0 else u'afternoon')
    data, flag = [], False
    shares, amount = 0, []
    s = '\n'.join([s.strip() for s in pre.stripped_strings]).split('\n')
    if s[0].find(u'之證券賣空成交量') != -1:
        for x in s:
            if x.find(u'非指定證券') != -1:
                break
            if x.find(u'錄得') != -1:
                flag = False
            if flag:
                x = [i.strip().replace(',', '').encode('utf8') for i in x.split(' ') if len(i) > 0]
                if len(x):
                    x[0] = x[0].strip('%').zfill(5)
                    data.append(x)
            elif x.find(u'代號') != -1:
                flag = True
            elif x.find(u'賣空交易成交股數') != -1:
                shares = int(x.split(':')[1].strip().replace(',', ''))
            elif x.find(u'賣空交易成交金額') != -1:
                amount.append([i.replace(',', '').encode('utf8') for i in x.split(':')[1].split(' ') if len(i) > 0])

        with open(fname, 'w') as fp:
            fp.write('share;%d\n' % shares)
            for x in amount:
                fp.write('amount;%s;%s\n' % tuple(x))
            for x in data:
                x.pop(1)
                fp.write(';'.join(x) + '\n')

def run(ctx, html, kwargs):
    global today
    today = kwargs['today']
    p1 = Thread(target = gethtml, args = ('http://www.hkex.com.hk/chi/stat/smstat/ssturnover/ncms/MSHTMAIN_C.HTM', 0, 1))
    p2 = Thread(target = gethtml, args = ('http://www.hkex.com.hk/chi/stat/smstat/ssturnover/ncms/MSHTGEM_C.HTM', 0, 0))
    p3 = Thread(target = gethtml, args = ('http://www.hkex.com.hk/chi/stat/smstat/ssturnover/ncms/ASHTMAIN_C.HTM', 1, 1))
    p4 = Thread(target = gethtml, args = ('http://www.hkex.com.hk/chi/stat/smstat/ssturnover/ncms/ASHTGEM_C.HTM', 1, 0))
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p1.join()
    p2.join()
    p3.join()
    p4.join()

if __name__ == '__main__':
    run(None, None, {'today' : '20160315'})
