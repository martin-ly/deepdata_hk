#coding: utf8

import urllib, urllib2, re, sys, json, subprocess, time
from bs4 import BeautifulSoup, NavigableString

def run(ctx, html, kwargs):
    today = kwargs['today']
    y, m, d = today[:4], today[4:6], today[6:]
    today = '/'.join([d, m, y])
    lastyday = '/'.join([d, m, str(int(y)-1)])
    url = 'http://sdinotice.hkex.com.hk/di/NSSrchCorpList.aspx?sa1=cl&scsd=%s&sced=%s&sc=%d&src=MAIN&lang=ZH' % (lastyday, today, int(kwargs['code']))

    data = urllib2.urlopen(url).read()
    bs = BeautifulSoup(data, 'html5lib', from_encoding='big5')
    node = bs.find('a', text = u'所有披露權益通知')
    if node is None:
        ctx.onerror(u'找不到定位点')
        return

    path = node['href']
    url = 'http://sdinotice.hkex.com.hk/di/' + path

    data = urllib2.urlopen(url).read()
    bs = BeautifulSoup(data, 'html5lib', from_encoding='big5')

    rec_count = bs.find('span', id = 'lblRecCount')
    if rec_count == 0:      #无记录
        return

    anchor = bs.find('tr', class_='boldtxtw')
    if anchor is None:
        ctx.onerror(u'找不到定位点')
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

    idx, sidx, num, items = -1, [], 0, []
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
            num += 1

    for row in rows:
        print row.decode('utf8')
#    #输出文件
#    with open('%s.gfjm.tmp' % code, 'w') as fp:
#        for row in rows:
#            fp.write('%s\n' % '\1'.join(row))
#
#    #click任务文件
#    with open('%s.gfjm.click.all' % code, 'w') as fp:
#        json.dump(items, fp)

    #返回js的click元素的xpath表达式
    for item in items:
        print item.decode('utf8')
