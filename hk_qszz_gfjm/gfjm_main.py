#coding: utf8

import re, sys, json, subprocess, time
from bs4 import BeautifulSoup, NavigableString

def run(code):
    code = sys.argv[-1]
    bs = BeautifulSoup(open(code+'.gfjm.html'), 'html5lib', from_encoding='utf8')
    anchor = bs.find('tr', class_='boldtxtw')
    if anchor is None:
        ctx.onerror(u'找不到定位点')
        return

    lastdate = 0
    p = subprocess.Popen(['../hkexe/getdate.exe', '-s', code.split('/')[-1]], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
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
            if tds[idx].find('a', href = True):         #有日期的行
                #element_date = tds[idx].
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
                    items.append("//tr[@class='boldtxtw']/../tr[%d]/td[%d]/a" % (num+2, idx+1))     #生成需点击元素的xpath表达式
                    rows.append(row)
            num += 1

    #输出文件
    with open('%s.gfjm.tmp' % code, 'w') as fp:
        for row in rows:
            fp.write('%s\n' % ';'.join(row))

    #click任务文件
    with open('%s.gfjm.click.all' % code, 'w') as fp:
        json.dump(items, fp)

    #返回js的click元素的xpath表达式
    for item in items:
        print '%s' % item.decode('utf8')

if __name__ == '__main__':
    run(sys.argv[-1])
