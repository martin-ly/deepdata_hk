#coding: utf8

import re
from bs4 import BeautifulSoup

def run(ctx, html):
    bs = BeautifulSoup(open(html), 'html5lib', from_encoding='utf8')
