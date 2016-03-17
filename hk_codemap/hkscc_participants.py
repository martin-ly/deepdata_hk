#coding: utf8

import urllib, zmq, os, opencc
from multiprocessing import Process

today = None
EndPoint = 'tcp://127.0.0.1:9067'
fname = 'List_of_Current_HKSCC_Participants.CSV'

def server(day):
    total = 0
    s = zmq.Context().socket(zmq.REP)
    s.bind(EndPoint)

    cc = opencc.OpenCC('zht2zhs.ini')

    while True:
        obj = s.recv_pyobj()
        if isinstance(obj, int):
            total += obj
        elif isinstance(obj, dict):
            obj['sname'] = cc.convert(obj['tname'].decode('utf8'))
            with open('%s/codemap' % day, 'a+') as fp:
                fp.write(';'.join([obj['code'], obj['ename'], obj['tname'], obj['sname'], obj['addr'], obj['tel'], obj['fax'], obj['website'], obj['brokerno']]) + '\n')
            total -= 1
        else:
            continue
        s.send_pyobj('OK')
        if total == 0:
            s.close()
            break

def run(ctx, html, kwargs):
    global today
    today = kwargs['today']

    if os.path.exists('%s/codemap' % today):
        os.remove('%s/codemap' % today)

    Process(target = server, args = (today,)).start()

    urllib.urlretrieve('http://www.hkex.com.hk/CHI/PLW/csv/List_of_Current_HKSCC_Participants.CSV', fname)
    parseCSV(ctx)

def parseCSV(ctx):
    s = zmq.Context().socket(zmq.REQ)
    s.connect(EndPoint)

    #该文件采用utf16编码，并包含BOM头：0xFFFE
    with open(fname, 'rb') as fp:
        data = fp.read()[2:]
    data = data.decode('utf16').split('\n')
    rows = []
    for idx, row in enumerate(data):
        if idx == 0:
            continue
        row = [x.strip('" \r\n') for x in row.split('\t')]
        if len(row) != 14:
            continue

        params = {
            'code'      : row[0].encode('utf8').strip(),
            'ename'     : row[4].encode('utf8').strip(),
            'tname'     : row[5].encode('utf8').strip(),
            'addr'      : ' '.join([row[7], row[8], row[9], row[10]]).encode('utf8').strip(),
            'tel'       : row[11].encode('utf8').replace(' ', '').replace('-', '').strip(),
            'fax'       : row[12].encode('utf8').replace(' ', '').replace('-', '').strip(),
            'website'   : row[13].encode('utf8').strip(),
        }

        if ctx and params['code'][0] == 'B':    #只有B类才存在经纪编号
            code = params['code'][1:]
            params['code'] = code
            ctx.addtask(['check_participant.js', code + '.jjbh.html', params, 30, 'check_participant', u'%s - 参与者编号->经纪编号' % code])
        else:
            params['brokerno'] = ''
            s.send_pyobj(params)
            s.recv_pyobj()

    s.close()
    if ctx:
        ctx.onfinish([fname,])

if __name__ == '__main__':
    run(None, None, {'today':'20160316'})
    #parseCSV(None)
