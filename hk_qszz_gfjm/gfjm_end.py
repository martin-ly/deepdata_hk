#coding: utf8

import os, re, deephk, opencc
from bs4 import BeautifulSoup, NavigableString

cc = opencc.OpenCC('zht2zhs.ini')

def issascii(s):
    for c in s:
        if ord(c) >= 128:
            return False
    return True

def run(ctx, code, kwargs):
    code = kwargs['code']
    today = kwargs['today']

    try:
        with open('%s/%s.gfjm.tmp' % (today, code), 'r') as fp:
            main = fp.readlines()
    except:
        main = []
    main = [x.strip(' \t\r\n').split('\1') for x in main]

    output, tmpfiles = [], []
    for i, x in enumerate(main):
        fclick = '%s/%s.%d.gfjm.click.html' % (today, code, i+1)
        bs = BeautifulSoup(open(fclick), 'html5lib', from_encoding='utf8')

        #表格类型
        anchor = bs.find('span', id='lblCaption')
        if anchor is None:
            ctx.onerror(u'找不到定位点1[%s]' % fclick)
            x.append('None')
            #continue
        s = ''.join([unicode(ss).strip(' \t\r\n') for ss in anchor.stripped_strings])
        x.append(s.encode('utf8'))

        #股份类别
        anchor = bs.find('span', id='lblDClass')
        if anchor is None:
            ctx.onerror(u'找不到定位点2[%s]' % fclick)
            x.append('None')
            #continue
        s = ''.join([unicode(ss).strip(' \t\r\n') for ss in anchor.stripped_strings])
        if s == u'H股':
            s = u'H Shares'
        x.append(s.encode('utf8'))

        #英文名字
        anchor = bs.find('span', id='lblEngName')
        if anchor is None:
            x[0] = x[0].replace(';', '\\;')     #预防抓到的字段里面存在';'的情况
            result = re.search(r'(.+?)\((.+)\)', x[0])
            if result is None:  #无英文名，表示该持股者原始名字是英文名，其繁体中文和简体中文字段全部填英文名
                x.insert(1, x[0])
                x.insert(2, x[0])
            else:   #英文名和中文名混在一起的情况
                isp1eng = issascii(result.group(1))
                isp2eng = issascii(result.group(2))
                if isp1eng and isp2eng: #两部分都是英文
                    x.insert(1, x[0])
                    x.insert(2, x[0])
                elif isp1eng and not isp2eng:   #第一部分是英文，第二部分是繁中
                    x[0] = result.group(2)
                    sname = cc.convert(result.group(2).decode('utf8'))
                    x.insert(1, sname.encode('utf8'))
                    x.insert(2, result.group(1).encode('utf8'))
                elif isp2eng and not isp1eng:   #第一部分是繁中，第二部分是英文
                    x[0] = result.group(1)
                    sname = cc.convert(result.group(1).decode('utf8'))
                    x.insert(1, sname.encode('utf8'))
                    x.insert(2, result.group(2).encode('utf8'))
                else:   #两部分都是繁中
                    sname = cc.convert(x[0].decode('utf8'))
                    x.insert(1, sname.encode('utf8'))
                    x.insert(2, x[0])
        else:   #有英文名，表示其原始名字是繁体中文，第二个字段填简体中文，第三个字段填这里抓到的英文名
            sim_name = cc.convert(x[0].decode('utf8'))
            x.insert(1, sim_name.encode('utf8'))
            for e in anchor.parent.next_siblings:
                if not isinstance(e, NavigableString):
                    s = ''.join([unicode(ss).strip(' \t\r\n') for ss in e.stripped_strings])
                    s = ' '.join(re.split(r'\(.*?\)', s)).strip(' \t\r\n')
                    x.insert(2, s.encode('utf8'))

        output.append(x)
        tmpfiles.append(fclick)
        tmpfiles.append('%s/%s.%d.gfjm.click.png' % (today, code, i+1))

    print u'解析 %d 条数据' % len(output)
    deephk.save_gfjm(today, code, output)
    tmpfiles.append('%s/%s.gfjm.tmp' % (today, code))
    tmpfiles.append('%s/%s.gfjm.click' % (today, code))
    tmpfiles.append('%s/%s.gfjm.click.all' % (today, code))
    tmpfiles.append('%s/%s.gfjm.html' % (today, code))
    tmpfiles.append('%s/%s.gfjm.png' % (today, code))
    if ctx:
        ctx.onfinish(tmpfiles)

if __name__ == '__main__':
    run(None, '20160412/00010_gfjm.html', {'today' : '20160412', 'code' : '00010'})
