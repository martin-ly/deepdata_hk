#coding: utf8

import os
from bs4 import BeautifulSoup

def sort(fname):
    def cmp(e1, e2):
        d1 = int(e1.find('pd').string)
        d2 = int(e2.find('pd').string)
        return d2 - d1

    print '>>>', fname
    bs = BeautifulSoup(open(fname), 'xml')
    rows = bs.find_all('row')
    rows.sort(cmp)

    old_body = bs.find('body')
    new_body = bs.new_tag('body')

    for row in rows:
        new_body.append(row)

    old_body.replace_with(new_body)

    data = bs.prettify()
    with open(fname, 'w') as fp:
        fp.write(data)

def main():
    for root, dirs, files in os.walk('xml\\stockcode_trader'):
        for name in files:
            sort(os.path.join(root, name))

def test():
    sort(u'xml\\stockcode_trader\\E00009\\E00009_第一上海.xml'.encode('gbk'))

if __name__ == '__main__':
    main()
