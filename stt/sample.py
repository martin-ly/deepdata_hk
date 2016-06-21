#coding: utf8

import urllib, urllib2, urlparse, gzip, sys, cookielib

def GetUrl(url, path = '', header = None, postdata = None, rspinfo = [], opener = None):
    req = urllib2.Request(urlparse.urljoin(url, path),
        None if postdata is None else urllib.urlencode(postdata),
        {} if header is None else header)
    if opener:
        rsp = opener.open(req)
    else:
        rsp  = urllib2.urlopen(req)
    content_encoding = rsp.info().get('Content-Encoding')

    if content_encoding == 'gzip':
        data = gzip.GzipFile(mode = 'rb', fileobj = StringIO(rsp.read())).read()
    else:
        data = rsp.read()

    if len(rspinfo) == 0:
        return data

    ret = {'response-body' : data}
    for name in rspinfo:
        ret[name] = rsp.info().get(name)
    return ret

def test1():
    '''通联'''
    header = {
        'Authorization' : 'Bearer 1b94b4dc290ae221dd4e1686f723b2cdbbb109134b959b9287178a240e732e1e'
    }
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPSHandler(1), urllib2.HTTPCookieProcessor(cj))
    domain = 'https://api.wmcloud.com'
    url = '/data/v1/api/market/getMktEqud.json?field=&tradeDate=20150513'
    data = GetUrl(domain, url, header, opener = opener)
    with open('test.json', 'w') as fp:
        fp.write(data)

def test2():
    '''百度'''
    opener = urllib2.build_opener(urllib2.HTTPHandler(1))
    header = {
        "apikey" : "af7bddd4a503d3b0662dd1758595b6ef"
    }
    data = GetUrl('http://apis.baidu.com', '/apistore/stockservice/stock?stockid=sz000858&list=1', header, opener = opener)
    with open('test.json', 'w') as fp:
        fp.write(data)

def test3():
    '''新浪'''
    opener = urllib2.build_opener(urllib2.HTTPHandler(1))
    url = 'http://hq.sinajs.cn'
    data = GetUrl(url, '/list=sh601006', opener = opener)
    with open('test.sina', 'w') as fp:
        fp.write(data)

if __name__ == "__main__":
    test3()
