#coding: utf8

def save_qszz(today, page_today, code, data):
    with open(today + '/%s.qszz' % code, 'w') as fp:
        fp.write('date;%s\n' % (page_today,))
        for code, name, amount, percentage in data:
            fp.write('%s;%s;%s;%s\n' % (code.strip(), name.strip(), amount.replace(',', ''), str(percentage)))

def save_gfjm(today, code, data):
    if len(data) == 0:
        return
    with open(today + '/%s.gfjm' % code, 'w') as fp:
        for x in data:
            fp.write('%s\n' % ';'.join(x))

def savefile(data, fname):
    fp = open(fname, 'wb')
    fp.write(data)
    fp.close()
