#coding: utf8

import re, os
from bs4 import BeautifulSoup

def run(ctx, html, kwargs):
    # casperjs输出的文件已经是utf8编码，而不管在html文件头中指定的编码
    bs = BeautifulSoup(open(html), 'html5lib', from_encoding='utf8')
    trs = bs.find_all('tr', class_=re.compile(r'TableContentStyle\d{1}'))
    if len(trs) == 0:
        ctx.onerror('抓取的证券代码数量为0')
    for tr in trs:
        code = unicode(tr.find('td', align='Center').string).encode('utf8')
        name = unicode(tr.find('span').string).encode('utf8')
        if len(code) != 5 or int(code) == 0:
            ctx.onerror('证券代码非法：%s' % code)
        else:
            ctx.addtask(['qszz.js', code + '_qszz.html', {'code' : code}, 'qszz', '%s - 券商追踪' % name])
            ctx.addtask(['gfjm.js', code + '_gfjm.html', {'code' : code}, 'gfjm_end', '%s - 股份解码' % name])
    os.remove(html)

if __name__ == '__main__':
    run('20160203/stocklist.html')
