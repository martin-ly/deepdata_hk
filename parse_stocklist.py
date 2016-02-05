#coding: utf8

import re
from bs4 import BeautifulSoup

def run(ctx, html):
    # casperjs输出的文件已经是utf8编码，而不管在html文件头中指定的编码
    bs = BeautifulSoup(open(html), 'html5lib', from_encoding='utf8')
    trs = bs.find_all('tr', class_=re.compile(r'TableContentStyle\d{1}'))
    if len(trs) == 0:
        ctx.onerror(u'抓取的证券代码数量为0')
    for tr in trs:
        code = unicode(tr.find('td', align='Center').string)
        name = unicode(tr.find('span').string)
        if len(code) != 5 or int(code) == 0:
            ctx.onerror(u'证券代码非法：%s' % code)
        else:
            ctx.runjs(('deep.js', code + '_deep.html', [code, ], 'deep', u'抓取%s深度持股数据' % name))

if __name__ == '__main__':
    run('20160203/stocklist.html')
