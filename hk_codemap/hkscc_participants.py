#coding: utf8

import urllib

today = None
fname = 'List_of_Current_HKSCC_Participants.CSV'

def run(ctx, html, kwargs):
    global today
    today = kwargs['today']

    urllib.urlretrieve('http://www.hkex.com.hk/CHI/PLW/csv/List_of_Current_HKSCC_Participants.CSV', fname)
    parseCSV(ctx)

def parseCSV(ctx):
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
        code = row[0].encode('utf8').strip()
        rows.append(';'.join([code, row[4].encode('utf8').strip(), row[5].encode('utf8').strip(), ' '.join([row[7], row[8], row[9], row[10]]).encode('utf8').strip(), row[11].encode('utf8').strip().replace(' ', ''), row[12].encode('utf8').strip().replace(' ', ''), row[13].encode('utf8').strip()]))
        if ctx:
            ctx.addtask(['check_participant.js', code + '_jjbh.html', {'code' : code}, 30, 'check_participant', '%s - 参与者编号->经纪编号' % code])

    with open('hkscc.participants', 'w') as fp:
        for row in rows:
            fp.write('%s\n' % row)

if __name__ == '__main__':
    #run(None, None, {'today':'20160315'})
    parseCSV(None)
