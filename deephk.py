#coding: utf8

def save_json(today, code, data):
    with open(today + '/%s.qszz' % code, 'w') as fp:
        for code, name, amount in data:
            fp.write('%s, %s, %s\n' % (code.strip(), name.strip(), amount.replace(',', '')))
