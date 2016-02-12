#coding: utf8

import re
from bs4 import BeautifulSoup

def run(ctx, html):
    bs = BeautifulSoup(open(html), 'html5lib', from_encoding='utf8')
    anchor = bs.find(text=re.compile(r'Search Result'))
    if anchor is None:
        ctx.onerror('找不到定位点')
        return

    partners = []
    for node in anchor.next_siblings:
        if node.name == 'tr':
            l = []
            for s in node.strings:
                l.append(unicode(s))
            partners.append(tuple(l))
            if len(l) != 5:
                ctx.onerror('一行数据不是5条')

    print u'解析 %d 条数据' % len(partners)
    if len(partners) == 0:
        ctx.onerror('没有抓取到数据')
    return partners

if __name__ == '__main__':
    partners = run(None, '20160212/00001_deep.html')
    for p in partners:
        print p
