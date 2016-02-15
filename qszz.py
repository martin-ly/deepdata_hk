#coding: utf8

import re
from bs4 import BeautifulSoup

def run(ctx, html):
    bs = BeautifulSoup(open(html), 'html5lib', from_encoding='utf8')

    total, idx = 0, [-1, -1, -1]
    anchor = bs.find(text=re.compile(r'result list title'))
    if anchor is None:
        ctx.onerror('找不到定位点1')
        return
    tds = anchor.find_parent('tr').find_next_sibling('tr').find(text=re.compile(r'Header')).find_next_sibling('tbody').find('tr').find_all('td', recursive=False)
    total = len(tds)
    for i, col in enumerate(tds):
        colname = ''.join(unicode(x) for x in col.strings).strip().encode('utf8')
        if colname == '參與者編號':
            idx[0] = i
        elif colname == '中央結算系統參與者名稱(*即願意披露的投資者戶口持有人)':
            idx[1] = i
        elif colname == '持股量':
            idx[2] = i
    print idx
    raw_input()

    anchor = bs.find(text=re.compile(r'Search Result'))
    if anchor is None:
        ctx.onerror('找不到定位点2')
        return

    partners = []
    for node in anchor.next_siblings:
        if node.name == 'tr':
            l = []
            for s in node.strings:
                l.append(unicode(s))
            print l
            partners.append(tuple(l))
            if len(l) != 5:
                ctx.onerror('一行数据不是5条')

    print u'解析 %d 条数据' % len(partners)
    if len(partners) == 0:
        ctx.onerror('没有抓取到数据')
    return partners

if __name__ == '__main__':
    partners = run(None, '111.html')
    for p in partners:
        print p
