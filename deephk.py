#coding: utf8

def save_qszz(today, code, data):
    with open(today + '/%s.qszz' % code, 'w') as fp:
        for code, name, amount, percentage in data:
            fp.write('%s, %s, %s, %s\n' % (code.strip(), name.strip(), amount.replace(',', ''), str(percentage)))
