#coding: utf8

import urlparse, urllib, urllib2
from datetime import datetime

send_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
}

def savefile(content, fname):
    fp = open(fname, 'wb')
    fp.write(content)
    fp.close()

def GetUrl(url, path, headers = None, postdata = None, headinfo = []):
    now = datetime.now()
    print '----->', now.strftime('%Y-%m-%d %H:%M:%S.') + ('%03d' % (now.microsecond / 1000))

    allpath = urlparse.urljoin(url, path)
    if postdata is None:
        data = None
    else:
        data = urllib.urlencode(postdata)
    req = urllib2.Request(allpath, headers = headers, data = data)
    rsp  = urllib2.urlopen(req)
    content_encoding = rsp.info().get('Content-Encoding')

    if content_encoding == 'gzip':
        data = gzip.GzipFile(mode = 'rb', fileobj = StringIO(rsp.read())).read()
    else:
        data = rsp.read()

    if len(headinfo) == 0:
        return data

    ret = [data,]
    for name in headinfo:
        ret.append(rsp.info().get(name))
    return ret

url = 'http://sdinotice.hkex.com.hk'
path = '/di/NSSrchCorpList.aspx?sa1=cl&scsd=13/06/2015&sced=13/06/2016&sc=1&src=MAIN&lang=ZH'

opener = urllib2.build_opener(urllib2.HTTPHandler(1))
urllib2.install_opener(opener)
savefile(GetUrl(url, path, send_headers), 'test.html')
