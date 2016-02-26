#coding: utf8

import re, sys, json
from bs4 import BeautifulSoup, NavigableString, UnicodeDammit

def run(code):
    code = sys.argv[-1]
    bs = BeautifulSoup(open(code+'.gfjm.html'), 'html5lib', from_encoding='utf8')
    anchor = bs.find('tr', class_='boldtxtw')
    if anchor is None:
        ctx.onerror('找不到定位点')
        return

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
            if tds[idx].find('a', href = True):
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
        print '%s' % item

if __name__ == '__main__':
    run(sys.argv[-1])
