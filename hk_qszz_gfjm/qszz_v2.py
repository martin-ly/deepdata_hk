#coding: utf8

import sys, cookielib, urllib2
sys.path.append('..')
from utils import *
from bs4 import BeautifulSoup
from datetime import date, timedelta
import qszz

header = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Accept-Language' : 'zh-CN',
    'Accept' : 'text/html, application/xhtml+xml, */*',
    'Accept-Encoding' : 'gzip, deflate'
}

def run(ctx, html, kwargs):
    url = 'http://www.hkexnews.hk/sdw/search/search_sdw_c.asp'

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPHandler(0), urllib2.HTTPCookieProcessor(cj))
    data = GetUrl(url, header = header, opener = opener)

    bs = BeautifulSoup(data, 'html5lib', from_encoding='big5')
    form = bs.find('form', attrs = {'name' : 'mainform'})
    if form is None:
        ctx.onerror(u'找不到定位点1')
        return

    txt_today_d = form.find('input', id = 'txt_today_d')
    txt_today_m = form.find('input', id = 'txt_today_m')
    txt_today_y = form.find('input', id = 'txt_today_y')
    current_page = form.find('input', id = 'current_page')
    stock_market = form.find('input', id = 'stock_market')
    IsExist_Slt_Stock_Id = form.find('input', id = 'IsExist_Slt_Stock_Id')
    IsExist_Slt_Part_Id = form.find('input', id = 'IsExist_Slt_Part_Id')
    rdo_SelectSortBy = form.find('input', id = 'rdo_SelectSortBy')
    sessionToken = form.find('input', attrs = {'name' : 'sessionToken'})
    sel_ShareholdingDate_d = form.find('select', attrs = {'name' : 'sel_ShareholdingDate_d'})
    sel_ShareholdingDate_m = form.find('select', attrs = {'name' : 'sel_ShareholdingDate_m'})
    sel_ShareholdingDate_y = form.find('select', attrs = {'name' : 'sel_ShareholdingDate_y'})

    txt_today_d = txt_today_d['value'] if txt_today_d else ''
    txt_today_m = txt_today_m['value'] if txt_today_m else ''
    txt_today_y = txt_today_y['value'] if txt_today_y else ''
    current_page = current_page['value'] if current_page else ''
    stock_market = stock_market['value'] if stock_market else ''
    IsExist_Slt_Stock_Id = IsExist_Slt_Stock_Id['value'] if IsExist_Slt_Stock_Id else ''
    IsExist_Slt_Part_Id = IsExist_Slt_Part_Id['value'] if IsExist_Slt_Part_Id else ''
    rdo_SelectSortBy = rdo_SelectSortBy['value'] if rdo_SelectSortBy else ''
    sessionToken = sessionToken['value'] if sessionToken else ''

    sel_ShareholdingDate_d = sel_ShareholdingDate_d.find('option', selected = True) if sel_ShareholdingDate_d else ''
    sel_ShareholdingDate_m = sel_ShareholdingDate_m.find('option', selected = True) if sel_ShareholdingDate_m else ''
    sel_ShareholdingDate_y = sel_ShareholdingDate_y.find('option', selected = True) if sel_ShareholdingDate_y else ''

    sel_ShareholdingDate_d = sel_ShareholdingDate_d.string if sel_ShareholdingDate_d else ''
    sel_ShareholdingDate_m = sel_ShareholdingDate_m.string if sel_ShareholdingDate_m else ''
    sel_ShareholdingDate_y = sel_ShareholdingDate_y.string if sel_ShareholdingDate_y else ''

    if txt_today_d == '' or txt_today_m == '' or txt_today_y == '' or current_page == '' or stock_market == '' or sessionToken == '' or IsExist_Slt_Stock_Id == '' or IsExist_Slt_Part_Id == '' or rdo_SelectSortBy == '' or sel_ShareholdingDate_d == '' or sel_ShareholdingDate_m == '' or sel_ShareholdingDate_y == '':
        ctx.onerror(u'找不到定位点2: txt_today_d=%s&txt_today_m=%s&txt_today_y=%s&current_page=%s&stock_market=%s&sessionToken=%s&IsExist_Slt_Stock_Id=%s&IsExist_Slt_Part_Id=%s&rdo_SelectSortBy=%s&sel_ShareholdingDate_d=%s&sel_ShareholdingDate_m=%s&sel_ShareholdingDate_y=%s&' % (txt_today_d, txt_today_m, txt_today_y, current_page, stock_market, sessionToken, IsExist_Slt_Stock_Id, IsExist_Slt_Part_Id, rdo_SelectSortBy, sel_ShareholdingDate_d, sel_ShareholdingDate_m, sel_ShareholdingDate_y))
        return

    postdata = (
        ('txt_today_d', txt_today_d),
        ('txt_today_m', txt_today_m),
        ('txt_today_y', txt_today_y),
        ('current_page', current_page),
        ('stock_market', stock_market),
        ('sessionToken', sessionToken),
        ('IsExist_Slt_Stock_Id', IsExist_Slt_Stock_Id),
        ('IsExist_Slt_Part_Id', IsExist_Slt_Part_Id),
        ('rdo_SelectSortBy', rdo_SelectSortBy),
        ('sel_ShareholdingDate_d', sel_ShareholdingDate_d),
        ('sel_ShareholdingDate_m', sel_ShareholdingDate_m),
        ('sel_ShareholdingDate_y', sel_ShareholdingDate_y),
        ('txt_stock_code', kwargs['code']),
        ('txt_stock_name', ''),
        ('txt_ParticipantID', ''),
        ('txt_Participant_name', ''),
    )
    data = GetUrl(url, header = header, postdata = postdata, opener = opener)
    ctx.save(html, data)
    kwargs['file-encoding'] = 'big5'
    qszz.run(ctx, html, kwargs)
