#coding: utf8

import re, deephk
from bs4 import BeautifulSoup, NavigableString

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

        extra_elements = []
        #表格类型
        anchor = bs.find('span', id='lblCaption')
        if anchor is None:
            ctx.onerror('找不到定位点1[%s]' % fclick)
            continue
        s = ''.join([unicode(ss).strip(' \t\r\n') for ss in anchor.stripped_strings])
        extra_elements.append(s.encode('utf8'))

        #股份类别
        anchor = bs.find('span', id='lblDClass')
        if anchor is None:
            ctx.onerror('找不到定位点2[%s]' % fclick)
            continue
        s = ''.join([unicode(ss).strip(' \t\r\n') for ss in anchor.stripped_strings])
        extra_elements.append(s.encode('utf8'))

        #英文名字
        anchor = bs.find('span', id='lblEngName')
        if anchor is None:
            extra_elements.append('')
        else:
            for e in anchor.parent.next_siblings:
                if not isinstance(e, NavigableString):
                    s = ''.join([unicode(ss).strip(' \t\r\n') for ss in e.stripped_strings])
                    s = ' '.join(re.split(r'\(.*?\)', s)).strip(' \t\r\n')
                    extra_elements.append(s.encode('utf8'))

        x += extra_elements
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
    if ctx:
        ctx.onfinish(tmpfiles)

if __name__ == '__main__':
    run(None, '20160310/00001_gfjm.html', {'today' : '20160310', 'code' : '00001'})
