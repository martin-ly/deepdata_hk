#coding: utf8

import re, deephk, os
from bs4 import BeautifulSoup

def run(ctx, code, kwargs):
    code = kwargs['code']
    today = kwargs['today']
    with open('%s/%s.gfjm.tmp' % (today, code), 'r') as fp:
        main = fp.readlines()
    main = [x.strip(' \t\r\n').split(';') for x in main]

    output = []
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
        os.remove(fclick)
        os.remove('%s/%s.%d.gfjm.click.png' % (today, code, i+1))

    deephk.save_gfjm(today, code, output)
    os.remove('%s/%s.gfjm.tmp' % (today, code))
    os.remove('%s/%s.gfjm.click' % (today, code))
    os.remove('%s/%s.gfjm.click.all' % (today, code))
    os.remove('%s/%s.gfjm.html' % (today, code))
    os.remove('%s/%s.gfjm.png' % (today, code))

if __name__ == '__main__':
    run(None, '20160226/00007_gfjm.html', {'today' : '20160226'})
