#coding: utf8

import re, sys, json, subprocess, time
from bs4 import BeautifulSoup, NavigableString
import gfjm_end

sys.path.append('..')
from utils import *

header = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Accept-Language' : 'zh-CN',
    'Accept' : 'text/html, application/xhtml+xml, */*'
}

def run(ctx, html, kwargs):
    today = kwargs['today']
    y, m, d = today[:4], today[4:6], today[6:]
    today = '/'.join([d, m, y])
    lastyday = '/'.join([d, m, str(int(y)-1)])

    url = 'http://sdinotice.hkex.com.hk/di/NSSrchCorpList.aspx?sa1=cl&scsd=%s&sced=%s&sc=%d&src=MAIN&lang=ZH' % (lastyday, today, int(kwargs['code']))
    data = GetUrl(url, header = header)

    bs = BeautifulSoup(data, 'html5lib', from_encoding='big5')
    node = bs.find('a', text = u'所有披露權益通知')
    if node is None:
        ctx.onerror(u'找不到定位点1')
        return

    url = 'http://sdinotice.hkex.com.hk/di/' + node['href']
    data = GetUrl(url, header = header)

    bs = BeautifulSoup(data, 'html5lib', from_encoding='big5')
    rec_count = int(bs.find('span', id = 'lblRecCount').string)
    if rec_count == 0:      #无记录
        return

    anchor = bs.find('tr', class_='boldtxtw')
    if anchor is None:
        ctx.onerror(u'找不到定位点2')
        return

    lastdate = 0
    p = subprocess.Popen(['../hkexe/getdate.exe', '-s', kwargs['code']], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    deadline = time.time() + 10
    while time.time() < deadline and p.poll() == None:
        time.sleep(0.01)
    if p.poll() == None:
        print u'getdate超时'
        p.kill()
    else:
        out, _ = p.communicate()
        out = out.strip(' \t\r\n').lower()
        if out == 'null':
            lastdate = 19700101
        else:
            lastdate = int(out)

    idx, sidx, items = -1, [], []
    for i, s in enumerate(anchor.stripped_strings):
        if s.find(u'事件的日期') != -1:
            idx = i
        elif s.find(u'數目') != -1:
            sidx.append(i)
    rows = []
    if idx != -1:
        for tr in anchor.next_siblings:
            if isinstance(tr, NavigableString):
                continue
            tds = tr.find_all('td', recursive=False)
            row = []
            node = tds[idx].find('a', href = True)
            if node:         #有日期的行
                date = ''.join([unicode(x).strip(' \t\r\n') for x in tds[idx].stripped_strings]).split('/')     #日/月/年
                if len(date) != 3:
                    ctx.onerror(u'日期格式错误%s' % str(date))
                    continue
                date = '%04d%02d%02d' % (int(date[2]), int(date[1]), int(date[0]))
                if int(date) > lastdate:
                    for i, td in enumerate(tds):
                        if i in sidx:
                            s = ''.join([unicode(x).replace(',', '') for x in td.stripped_strings])
                        else:
                            s = ''.join([unicode(x) for x in td.stripped_strings])
                        row.append(s.encode('utf8'))
                    items.append(node['href'])     #生成需点击元素的链接地址
                    rows.append(row)

    #输出文件
    with open('%s/%s.gfjm.tmp' % (kwargs['today'], kwargs['code']), 'w') as fp:
        for row in rows:
            fp.write('%s\n' % '\1'.join(row))

    for idx, item in enumerate(items):
        url = 'http://sdinotice.hkex.com.hk/di/' + item
        data = GetUrl(url, header = header)
        fname = kwargs['today'] + '/' + kwargs['code'] + '.' + str(idx+1) + '.gfjm.click.html'
        with open(fname, 'w') as fp:
            fp.write(data)

    gfjm_end.run(ctx, None, kwargs)
