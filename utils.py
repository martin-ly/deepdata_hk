#coding: utf8

import urllib, urllib2, urlparse, gzip, sys

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
