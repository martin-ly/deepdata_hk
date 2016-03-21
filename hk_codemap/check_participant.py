#coding: utf8

import re, zmq, os.path
from hkscc_participants import EndPoint
from bs4 import BeautifulSoup, NavigableString
from main import OUTPUT

def run(ctx, html, kwargs):
    folder = os.path.join(os.path.dirname(__file__), kwargs['today'])
    fname = kwargs['today'] + '/' + kwargs['code']+'.jjbh.html'
    bs = BeautifulSoup(open(fname), 'html5lib', from_encoding='utf8')
    kwargs['code'] = 'B' + kwargs['code']
    anchor = bs.find('td', text = re.compile(u'.*經紀代號.*'))
    if anchor is None:
        ctx.onerror(u'找不到定位点')
        kwargs['brokerno'] = 'None'
    else:
        anchor = anchor.next_sibling
        l = ''.join([x.strip().encode('utf8') for x in anchor.stripped_strings if len(x) > 0]).split(', ')
        kwargs['brokerno'] = ','.join(x for x in l if len(l) > 0)

    s = zmq.Context().socket(zmq.REQ)
    s.connect(EndPoint)
    s.send_pyobj(kwargs)
    s.recv_pyobj()
    s.close()
    ctx.onfinish([fname, fname + '.png'])
    ctx.set_output(OUTPUT.FOLDER, folder)
    return kwargs

if __name__ == '__main__':
    params = {
        'code'      : '01089',
        'ename'     : 'sssss',
        'tname'     : 'ttttt',
        'addr'      : 'xxxxx',
        'tel'       : '1234567',
        'fax'       : '7654321',
        'website'   : 'www.nnn.com',
    }
    print run(None, None, params)
