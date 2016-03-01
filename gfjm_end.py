#coding: utf8

import re, deephk
from bs4 import BeautifulSoup

def run(ctx, code, kwargs):
    code = kwargs['code']
    today = kwargs['today']
    try:
        with open('%s/%s.gfjm.tmp' % (today, code), 'r') as fp:
            main = fp.readlines()
    except:
        main = []
    main = [x.strip(' \t\r\n').split(';') for x in main]

    output, tmpfiles = [], []
    for i, x in enumerate(main):
        fclick = '%s/%s.%d.gfjm.click.html' % (today, code, i+1)
        bs = BeautifulSoup(open(fclick), 'html5lib', from_encoding='utf8')
        anchor = bs.find('span', id='lblCaption')
        if anchor is None:
            ctx.onerror('找不到定位点[%s]' % fclick)
            continue
        s = ''.join([unicode(ss).strip(' \t\r\n') for ss in anchor.stripped_strings])
        x.append(s.encode('utf8'))
        output.append(x)
        tmpfiles.append(fclick)
        tmpfiles.append('%s/%s.%d.gfjm.click.png' % (today, code, i+1))

    print '解析 %d 条数据' % len(output)
    deephk.save_gfjm(today, code, output)
    tmpfiles.append('%s/%s.gfjm.tmp' % (today, code))
    tmpfiles.append('%s/%s.gfjm.click' % (today, code))
    tmpfiles.append('%s/%s.gfjm.click.all' % (today, code))
    tmpfiles.append('%s/%s.gfjm.html' % (today, code))
    tmpfiles.append('%s/%s.gfjm.png' % (today, code))
    ctx.onfinish(tmpfiles)

if __name__ == '__main__':
    run(None, '20160226/90005_gfjm.html', {'today' : '20160226', 'code' : '90005'})
