#coding: utf8

import re, sys
from bs4 import BeautifulSoup

def run(ctx, html, kwargs):
    codes = getattr(sys.modules[__package__], "codes", [])
    # casperjs输出的文件已经是utf8编码，而不管在html文件头中指定的编码
    bs = BeautifulSoup(open(html), 'html5lib', from_encoding='utf8')
    trs = bs.find_all('tr', class_=re.compile(r'TableContentStyle\d{1}'))
    if len(trs) == 0:
        ctx.onerror(u'抓取的证券代码数量为0')
    count = 0
    for tr in trs:
        code = unicode(tr.find('td', align='Center').string).encode('utf8')
        name = unicode(tr.find('span').string)
        if len(code) != 5 or int(code) == 0:
            ctx.onerror(u'证券代码非法：%s' % code)
        else:
            if len(codes) != 0 and code not in codes:
                continue
            ctx.addtask(['qszz.js', code + '_qszz.html', {'code' : code}, 30, 'qszz', u'%s - 券商追踪' % name])
            ctx.addtask(['gfjm.js', code + '_gfjm.html', {'code' : code}, 300, 'gfjm_end', u'%s - 股份解码' % name])
    ctx.onfinish([html,])

if __name__ == '__main__':
    run('20160203/stocklist.html')
