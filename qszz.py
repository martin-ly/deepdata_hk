#coding: utf8

import re, deephk
from bs4 import BeautifulSoup

def run(ctx, html, kwargs):
    bs = BeautifulSoup(open(html), 'html5lib', from_encoding='utf8')

    total, idx = 0, [-1, -1, -1, -1]
    anchor = bs.find(text=re.compile(r'result list title'))
    if anchor is None:
        ctx.onerror('找不到定位点1')
        return
    tds = anchor.find_parent('tr').find_next_sibling('tr').find(text=re.compile(r'Header')).find_next_sibling('tbody').find('tr').find_all('td', recursive=False)
    total = len(tds)
    if total < 3:
        ctx.onerror('数据不足3列，请检查页面')
        return
    for i, col in enumerate(tds):
        colname = ''.join(unicode(x) for x in col.strings).strip().encode('utf8')
        if colname.find('參與者編號') != -1:
            idx[0] = i
        elif colname.find('中央結算系統參與者名稱') != -1:
            idx[1] = i
        elif colname.find('持股量') != -1:
            idx[2] = i
        elif colname.find('百份比') != -1:
            idx[3] = i
    if idx[0] == -1 or idx[1] == -1 or idx[2] == -1:
        ctx.onerror('没有找到合适的数据列: %s' % idx)
        return

    anchor = bs.find(text=re.compile(r'Search Result'))
    if anchor is None:
        ctx.onerror('找不到定位点2')
        return

    partners = []
    for node in anchor.next_siblings:
        if node.name == 'tr':
            l = []
            for i, s in enumerate(node.strings):
                if i in idx:
                    l.append(unicode(s).encode('utf8'))
            if idx[3] == -1:
                l.append(None)
            partners.append(tuple(l))
            if len(l) != 4:
                if ctx is None:
                    print '一行数据不是4条'
                else:
                    ctx.onerror('一行数据不是4条')

    print '解析 %d 条数据' % len(partners)
    if len(partners) == 0:
        ctx.onerror('没有抓取到数据')
    else:
        deephk.save_qszz(kwargs['today'], kwargs['code'], partners)
    return partners

if __name__ == '__main__':
    partners = run(None, '111.html', {'today' : '20160224', 'code' : '01153'})
    for p in partners:
        print p
